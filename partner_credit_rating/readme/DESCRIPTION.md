Provider agnostic credit rating of companies.

Ratings are stored in a dedicated `credit.rating` model linked to the
commercial partner (no extra column on `res_partner`): normalized score from
0 to 100, risk level and the company reference at the provider. Provides a
search wizard to identify the company (name, tax ID, company ID, country) and
a scheduled action to refresh monitored companies.

Providers are implemented in separate modules, e.g.
`partner_credit_rating_allianz`. Use the `_rating_changed()` hook of
`credit.rating` to react to a rating change (sale blocking, payment terms...).
