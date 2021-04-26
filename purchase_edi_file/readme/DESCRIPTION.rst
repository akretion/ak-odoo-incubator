This module allows to send file to supplier on purchase order's validation.
The file may be sent by mail or using a backend storage (aws, sftp, ...)
The file comes from native Odoo exports but other format could be implemented

The format of the file may depend on the product and the supplier or on the supplier only
(meaning we may have multiple files for a same PO, depending on the products)
