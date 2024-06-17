import sys
import importlib

MOVED_MODULES = {
    "odoo.addons.sale.models.sale_order_line": "odoo.addons.sale.models.sale",
    "odoo.addons.sale.models.sale_order": "odoo.addons.sale.models.sale",
}
EXTENDED_MODULES = ["odoo.tools.float_utils", "odoo.http"]


def extend(module, name):
    extended_module = importlib.import_module(f"odoo.addons.sixteen_in_fourteen.{name}")
    module.__dict__.update(
        {
            key: value
            for key, value in extended_module.__dict__.items()
            if key not in ["__file__", "__doc__", "__package__", "__loader__"]
        }
    )


class SixteenInFourteenMovedHook(object):
    def find_module(self, name, path=None):
        if name in MOVED_MODULES:
            return self

    def load_module(self, name):
        assert name not in sys.modules
        odoo_module = sys.modules.get(name)
        if not odoo_module:
            odoo_module = importlib.import_module(MOVED_MODULES[name])
        sys.modules[name] = odoo_module
        return odoo_module


class SixteenInFourteenExtendedHook(object):
    def find_module(self, name, path=None):
        if name in EXTENDED_MODULES:
            return self

    def load_module(self, name):
        assert name not in sys.modules
        odoo_module = sys.modules.get(name)
        if not odoo_module:
            odoo_module = importlib.import_module(name)
            extend(odoo_module, name)

        sys.modules[name] = odoo_module
        return odoo_module


sys.meta_path.insert(0, SixteenInFourteenMovedHook())
sys.meta_path.insert(0, SixteenInFourteenExtendedHook())

# Also patch already imported modules
for mod in EXTENDED_MODULES:
    if mod in sys.modules:
        extend(sys.modules[mod], mod)
