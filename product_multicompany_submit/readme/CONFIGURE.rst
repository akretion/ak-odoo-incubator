1. Add users to approval group
2. Add users to submittal groups
3. Users in submittal groups use the new menu items to submit a product
4. Users in approval groups approve the products to make them multicompany

In order to test it, note the following:
  - This module only works in multi-company, multi-catalogue mode.
  - Because product submittal states are tracked and messages are generated, users need an email address on their partner form
  - After installing, you will need to update existing products' fields **state_multicompany_submit** and **multicompany_origin_company_id**
