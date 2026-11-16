This module stores one rating per company. Several providers per company can be added by an extra
module, e.g. `partner_credit_rating_multi`, without changing this one:

- `credit.rating`: redefine `_partner_uniq` with the same name as
  `unique(partner_id, provider)`.
- `res.partner._get_credit_rating(provider)`: do not reuse the rating of
  another provider, always create a new one.
- `res.partner._get_main_credit_rating()`: return the rating with the worst
  risk (then the most recent), so that `credit_risk` shows the worst one.
- `res.partner.credit_risk`: make it computed with an exact search method on
  the worst risk (the default search matches any rating of the company).
- Search wizard: show the `provider` field (hidden here).
- Partner form: show the number of ratings and open the list when several.
- Settings: the company provider becomes the default provider of the wizard.
