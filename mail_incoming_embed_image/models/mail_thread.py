# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        # In Odoo the embed (cid) images are converted in message_post, so after
        # the create. It means that if the description (field containing usually the
        # body of the mail) is not synchronized after creation, it is wrong (does not
        # display the emebed images). Also, in some case a notification could be sent
        # by mail using mail.template with _track_template for instance, and this is
        # done before the message_post of the content, so usually without the images.

        # That is why we try to convert it right before creation to avoid all issues
        # of undisplayed images.
        # mandatory fields for _message_post_process_attachments
        attachment_ids = []
        if msg_dict.get("attachments", []):
            msg_dict["model"] = self._name
            msg_dict["res_id"] = 0
            attachment_values = self._message_post_process_attachments(
                msg_dict["attachments"], False, msg_dict
            )
            # the format returned by _message_post_process_attachments is [(4, id)]
            attachment_ids = [x[1] for x in attachment_values.pop("attachment_ids")]
            if not msg_dict.get("attachment_ids"):
                msg_dict["attachment_ids"] = []
            msg_dict["attachment_ids"] += attachment_ids
            # in case body did change
            old_body = msg_dict.get("body", "")
            msg_dict.update(attachment_values)
            # remove this at it is not expected then for message_post
            msg_dict.pop("model")
            msg_dict.pop("res_id")
            # remove attachment since it now has been created and added to
            # attachment_ids
            msg_dict.pop("attachments")

            # The body could have been set in a custom value already, line it is common
            # to do it before the super of message_new in the message implementing
            # the feature (like it is in helpdesk_mgmt for instance)
            # so we check all fields containing the old body and replace by the new
            # one (with images converted)
            if attachment_values.get("body"):
                for field_name, val in custom_values.items():
                    if isinstance(val, str) and old_body in val:
                        custom_values[field_name] = custom_values[field_name].replace(
                            old_body, msg_dict["body"]
                        )
        res = super().message_new(msg_dict, custom_values=custom_values)
        # fix the res_id as it was set to 0, before creation as we could not have
        # the id, because _message_post_process_attachments is designed to be called
        # on message_post, with is designed to be called on already created record
        if attachment_ids:
            self.env["ir.attachment"].browse(attachment_ids).write({"res_id": res.id})
        return res
