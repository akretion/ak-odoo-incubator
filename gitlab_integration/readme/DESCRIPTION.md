This modules adds GitLab integration to odoo.

For now it supports:

- Listing related GitLab Merge Requests in Odoo Project Tasks from a Odoo Task ids in
  the GitLab Merge Request title: e.g., a GitLab Merge Request titled "[2,124] Fix issue
  with user login" will be linked to the Odoo Task with id 2124. Syntax is "[id1][id2]
  ... Title", only existing ids before the title will be considered.
- Synchronizing from existing GitLab Projects
- Setting up webhooks for GitLab projects
- Automatic processing of Merge Request events from GitLab webhooks
