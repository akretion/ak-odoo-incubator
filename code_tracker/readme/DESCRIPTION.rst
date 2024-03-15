To be able to see what functions is called or not you should when you install this module :
- Install this module in the manifest
- Add at the beginning of the model from odoo.addons.code_tracker.decorators import tracker_code
- Add the decorator above the called function

To see the list of the called functions :
- Go to settings --> technical --> tracker trace
