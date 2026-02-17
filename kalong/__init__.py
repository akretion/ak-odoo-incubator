from os import environ
from . import controllers
from . import models

environ["KALONG_HOST"] = "localhost"
environ["KALONG_PORT"] = "25846"
environ["KALONG_FRONT_HOST"] = "eighteen.localhost"
environ["KALONG_FRONT_PORT"] = "80"
environ["KALONG_BASE_PATH"] = "/kalong"
# environ["KALONG_LOG"] = "debug"
# environ["KALONG_NO_BROWSER"] = "1"
environ["PYTHONBREAKPOINT"] = "odoo.addons.kalong.breakpoint"


def breakpoint():  # pylint: disable=redefined-builtin
    import sys
    import threading

    from kalong.stepping import add_step, start_trace, stop_trace

    if getattr(threading.current_thread(), "testing", False):
        from odoo.modules.registry import DummyRLock, Registry

        # In test mode we must unlock Registry lock
        if not isinstance(Registry._lock, DummyRLock):
            Registry._lock = DummyRLock()

    frame = sys._getframe().f_back
    stop_trace(frame)
    add_step("step", frame)
    start_trace(frame)
