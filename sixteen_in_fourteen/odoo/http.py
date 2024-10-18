# Part of Odoo. See LICENSE file for full copyright and licensing details.

import collections.abc
from abc import ABC, abstractmethod

import werkzeug.exceptions

_dispatchers = {}
CORS_MAX_AGE = 60 * 60 * 24


class Dispatcher(ABC):
    routing_type: str

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        _dispatchers[cls.routing_type] = cls

    def __init__(self, request):
        self.request = request

    @classmethod
    @abstractmethod
    def is_compatible_with(cls, request):
        """
        Determine if the current request is compatible with this
        dispatcher.
        """

    def pre_dispatch(self, rule, args):
        """
        Prepare the system before dispatching the request to its
        controller. This method is often overridden in ir.http to
        extract some info from the request query-string or headers and
        to save them in the session or in the context.
        """
        routing = rule.endpoint.routing
        self.request.session.can_save = routing.get("save_session", True)

        set_header = self.request.future_response.headers.set
        cors = routing.get("cors")
        if cors:
            set_header("Access-Control-Allow-Origin", cors)
            set_header(
                "Access-Control-Allow-Methods",
                (
                    "POST"
                    if routing["type"] == "json"
                    else ", ".join(routing["methods"] or ["GET", "POST"])
                ),
            )

        if cors and self.request.httprequest.method == "OPTIONS":
            set_header("Access-Control-Max-Age", CORS_MAX_AGE)
            set_header(
                "Access-Control-Allow-Headers",
                "Origin, X-Requested-With, Content-Type, Accept, Authorization",
            )
            werkzeug.exceptions.abort(Response(status=204))

    @abstractmethod
    def dispatch(self, endpoint, args):
        """
        Extract the params from the request's body and call the
        endpoint. While it is preferred to override ir.http._pre_dispatch
        and ir.http._post_dispatch, this method can be override to have
        a tight control over the dispatching.
        """

    def post_dispatch(self, response):
        """
        Manipulate the HTTP response to inject various headers, also
        save the session when it is dirty.
        """
        self.request._save_session()
        self.request._inject_future_response(response)
        root.set_csp(response)

    @abstractmethod
    def handle_error(self, exc: Exception) -> collections.abc.Callable:
        """
        Transform the exception into a valid HTTP response. Called upon
        any exception while serving a request.
        """
