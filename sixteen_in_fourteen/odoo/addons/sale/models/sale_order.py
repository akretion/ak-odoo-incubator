# Part of Odoo. See LICENSE file for full copyright and licensing details.

READONLY_FIELD_STATES = {
    state: [("readonly", True)] for state in {"sale", "done", "cancel"}
}

LOCKED_FIELD_STATES = {state: [("readonly", True)] for state in {"done", "cancel"}}

INVOICE_STATUS = [
    ("upselling", "Upselling Opportunity"),
    ("invoiced", "Fully Invoiced"),
    ("to invoice", "To Invoice"),
    ("no", "Nothing to Invoice"),
]
