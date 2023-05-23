To be able to see what functions is called or not you should when you install this module :
- install this module in the manifest
- Add at the beginning of the model from odoo.addons.code_tracker.decorators import tracker_code
- add the decorator above the called function

to see the list of the called functions :
- go to settings --> technical --> tracker trace
