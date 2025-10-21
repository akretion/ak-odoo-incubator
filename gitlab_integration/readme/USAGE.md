In Odoo, setup a fastapi endpoint with gitlab as app, GitLab API as user and create a
secret token.

Then, in GitLab, go to your project settings, navigate to "Webhooks", and add the Odoo
endpoint URL. Use the secret token you created in Odoo for authentication.

For now, only the "Merge Request Events" are supported. Make sure to select this event
when setting up the webhook in GitLab.
