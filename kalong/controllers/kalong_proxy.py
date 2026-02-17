# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import selectors
import threading

import requests
from werkzeug.exceptions import HTTPException

from odoo import http
from odoo.tools import config

from odoo.addons.bus.websocket import (
    CloseCode,
    ConnectionState,
    ServiceUnavailable,
    TimeoutManager,
    Websocket,
    WebsocketConnectionHandler,
)

_logger = logging.getLogger(__name__)

try:
    from websocket import WebSocket as WebSocketClient
except ImportError:
    WebSocketClient = None
    _logger.warning(
        "WebSocket support is not available, "
        "please install the websocket-client package"
    )


class KalongProxy(http.Controller):
    @http.route("/kalong/<path:path>", type="http", auth="user", save_session=False)
    def kalong(self, path, **kw):
        if WebSocketClient is None:
            return http.request.make_response(
                "WebSocket support is not available",
                headers={"Content-Type": "text/plain"},
                status=503,
            )
        http_request = http.request.httprequest
        # Proxy request to kalong
        response = requests.get(
            f"http://localhost:25846/kalong/{path}",
            headers=dict(http_request.headers),
            timeout=10,
        )
        return http.request.make_response(
            response.content,
            headers=dict(response.headers),
            status=response.status_code,
        )

    @http.route(
        "/kalong/<path:path>",
        type="http",
        auth="user",
        csrf=False,
        websocket=True,
        save_session=False,
    )
    def broadcast_channel(self, path, **kwargs):
        """Websocket route to handle broadcast channel connections."""
        return KalongWebsocketConnectionHandler.open_connection(http.request, path)


class ProxyWebSocket(Websocket):
    def __init__(self, sock, session, cookies, path):
        super().__init__(sock, session, cookies)

        self.kalong_websocket = WebSocketClient()
        self.kalong_websocket.connect(f"ws://localhost:25846/kalong/{path}")

        self._Websocket__selector.register(
            self.kalong_websocket.sock, selectors.EVENT_READ
        )

    def proxy(self):
        while self.state is not ConnectionState.CLOSED:
            try:
                readables = {
                    selector_key[0].fileobj
                    for selector_key in self._Websocket__selector.select(
                        TimeoutManager.TIMEOUT
                    )
                }
                if (
                    self._timeout_manager.has_keep_alive_timed_out()
                    and self.state is ConnectionState.OPEN
                ):
                    self.disconnect(CloseCode.KEEP_ALIVE_TIMEOUT)
                    continue
                if self._timeout_manager.has_frame_response_timed_out():
                    self._terminate()
                    continue
                if not readables and self._timeout_manager.should_send_ping_frame():
                    self._send_ping_frame()
                    continue
                if self._Websocket__notif_sock_r in readables:
                    self._dispatch_bus_notifications()
                if self._Websocket__socket in readables:
                    message = self._process_next_message()
                    if message is not None:
                        self.kalong_websocket.send(message)
                if self.kalong_websocket.sock in readables:
                    message = self.kalong_websocket.recv()
                    if message is not None:
                        self._send(message)

            except Exception as exc:
                self._handle_transport_error(exc)


class KalongWebsocketConnectionHandler(WebsocketConnectionHandler):
    @classmethod
    def websocket_allowed(cls, request):
        return True  # Allow WebSocket connections in test mode for Kalong

    @classmethod
    def _serve_forever(cls, websocket, db, httprequest, path):
        current_thread = threading.current_thread()
        current_thread.type = "websocket"

        websocket.proxy()

    @classmethod
    def open_connection(cls, request, path):
        if not cls.websocket_allowed(request):
            raise ServiceUnavailable("Websocket is disabled in test mode")
        public_session = cls._handle_public_configuration(request)
        try:
            response = cls._get_handshake_response(request.httprequest.headers)
            socket = request.httprequest._HTTPRequest__environ["socket"]
            session, db, httprequest = (
                (public_session or request.session),
                request.db,
                request.httprequest,
            )
            response.call_on_close(
                lambda: cls._serve_forever(
                    ProxyWebSocket(socket, session, httprequest.cookies, path),
                    db,
                    httprequest,
                    "",
                )
            )
            # Force save the session. Session must be persisted to handle
            # WebSocket authentication.
            request.session.is_dirty = True
            return response
        except KeyError as exc:
            raise RuntimeError(
                "Couldn't bind the websocket. Is the connection opened on"
                f" the evented port ({config['gevent_port']})?"
            ) from exc
        except HTTPException as exc:
            # The HTTP stack does not log exceptions derivated from the
            # HTTPException class since they are valid responses.
            _logger.error(exc)
            raise
