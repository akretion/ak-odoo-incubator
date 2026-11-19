This module is waiting for a such call

```python
    # this variable may contains data which can be used in your template
    my_params = {}

    # data4print content: tuple of product.product record, quantity
    # if data4print is False then active_ids records are used.
    # Check your label template placeholder match with these records
    self._get_zebra_labels(data4print, content_params=my_params)

```

label_wizard call it in a such way without depsnds ont it

This module is primarly linked to product.product model

For use it, you have to set this kind of code:

```python

PRINTER_NAME = "label"


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_raw_printer_label_template(self, content_params):
        res = super()._get_raw_printer_label_template(content_params)
        return get_template(content_params)

    def _get_printer_name(self):
        # This is the default printer name for basic cases
        return PRINTER_NAME


def get_template(content_params):
    record = content_params.get("record")
    if not record:
        raise exceptions.UserError("No record provided for label template generation")
    # ^FX is comment
    return f"""^XA
^FX utf8
^CI28
^FX taille police
^CF0,40

^FX l1: product code
^FO660,50^FD{record.default_code}^FS

^XZ"""

```

This module is firsly for printing with local printers.

But if you want manage other case, your may define this method


```python
def _get_network_printer_by_usage():
    super()._get_network_printer_by_usage()
    return {"usageA": "printer1", "usageB": "printer2"}

```


To work with other models, you need to add that code:


```python
class MyModel(models.Model):
    _name = "my.model"
    _inherit = [_name, "printable.mixin"]

```
