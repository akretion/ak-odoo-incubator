# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.service.server import (
    _logger,
    CommonServer,
    ThreadedServer,
    GeventServer,
    PreforkServer,
)

CommonServer._on_stop_funcs = []


def on_stop(self, func):
    """Register a cleanup function to be executed when the server stops"""
    self._on_stop_funcs.append(func)


def stop(self):
    for func in self._on_stop_funcs:
        try:
            _logger.debug("on_close call %s", func)
            func()
        except Exception:
            _logger.warning("Exception in %s", func.__name__, exc_info=True)


CommonServer.on_stop = classmethod(on_stop)
CommonServer.stop = stop


# Call super() in the stop method of the server classes
for cls in (ThreadedServer, GeventServer, PreforkServer):

    def stop(self, cls=cls, old_stop=cls.stop):
        super(cls, self).stop()
        old_stop(self)

    cls.stop = stop
