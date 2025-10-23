In Odoo, setup a fastapi endpoint with gitlab as app, GitLab API as user and create a
secret token.

Then, in GitLab, go to your project settings, navigate to "Webhooks", and add the Odoo
endpoint URL. Use the secret token you created in Odoo for authentication.

For now, only the "Merge Request Events" are supported. Make sure to select this event
when setting up the webhook in GitLab.

When a merge request is created or updated in GitLab, the webhook will send the event to
Odoo, which will then process it and link it to the corresponding project task.

You can also synchronize existing GitLab projects with Odoo to ensure all relevant merge requests
are linked to their respective tasks and automatically set up webhooks for them.

In order to do that, in debug mode, go to Projects > Configuration > GitLab > Synchronize Projects and follow the wizard instructions.
