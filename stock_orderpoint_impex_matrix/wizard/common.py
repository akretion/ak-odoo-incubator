#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from collections import OrderedDict

MAPPING_COLUMNS_PER_WH = OrderedDict(
    [
        ("qty_available", "Quantité actuelle"),
        ("product_min_qty", "Quantité minimale"),
        ("product_max_qty", "Quantité maximale"),
        ("lead_days", "Délai fournisseur"),
        ("qty_multiple", "Quantité multiple de"),
    ]
)
LEN_COLUMNS_PER_WH = len(MAPPING_COLUMNS_PER_WH)
ROW_START_PRODUCTS = 3
PREFIX_HEADER_WH = "Entrepôt "
COLUMN_START_WH_BLOCKS = 3
ROW_MAX_STYLING = 1000
