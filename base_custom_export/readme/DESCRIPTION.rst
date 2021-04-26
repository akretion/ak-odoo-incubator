This module allow easily export data into an attachment, using Odoo native exporting tool.
Its meant to be used by submodules needing to export data and add the following features :
- Easily re-order the fields to export (actually comes from base_export_manager module)
- Allow to customize the fields label to have a fully customizable header
- Allow to customize the filename
- Allow to add more data (not from fields), this module implement the possibility to add static data
but it can easily be extended to add more complex logic to get some advanced custom data

It supports csv and xlsx format but other one could easily be added
