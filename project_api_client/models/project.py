# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# Sébastien Beau <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8106

import logging
import urllib

import requests
from lxml import etree
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


ISSUE_DESCRIPTION = _(
    """<h4>What doesn't works ?</h4>
<br/>
<br/>
<br/>
<h4>Here is how it should work ?</h4>
<br/>
""")
ERROR_MESSAGE = _("There is an issue with support. Please send an email")


class ExternalTask(models.Model):
    _name = "external.task"
    _description = "External task"

    def _get_select_project(self):
        # solve issue during installation and test
        # If we have an uid it's a real call from webclient
        if self._context.get("uid"):
            return self._call_odoo("project_list", {})
        else:
            return []

    def _get_select_type(self):
        # solve issue during installation and test
        # If we have an uid it's a real call from webclient
        if self._context.get("uid"):
            return self._call_odoo("type_list", {})
        else:
            return []

    name = fields.Char("Name")
    stage_name = fields.Char("Stage")
    description = fields.Html(
        "Description", default=lambda self: _(ISSUE_DESCRIPTION)
    )
    message_ids = fields.One2many(
        comodel_name="external.message", inverse_name="res_id"
    )
    create_date = fields.Datetime("Create Date", readonly=True)
    priority = fields.Selection(
        [("0", "Low"), ("1", "Normal"), ("2", "High")], default="1"
    )
    date_deadline = fields.Datetime("Délai", readonly=True)
    author_id = fields.Many2one("res.partner", string="Author", readonly=True)
    assignee_id = fields.Many2one(
        "res.partner", string="Assignee name", readonly=True
    )
    origin_name = fields.Char()
    origin_url = fields.Char()
    origin_db = fields.Char()
    origin_model = fields.Char()
    project_id = fields.Selection(
        selection=_get_select_project, string="Project"
    )
    color = fields.Integer(string="Color Index")
    tag_ids = fields.Selection(selection=_get_select_type, string="Type")
    attachment_ids = fields.One2many(
        comodel_name="external.attachment", inverse_name="res_id"
    )
    to_invoice = fields.Boolean(readonly=True)
    customer_report = fields.Html(readonly=True)
    customer_kanban_report = fields.Html(readonly=True)

    def get_url_key(self):
        self = self.sudo()
        res = {
            "url": self.env["ir.config_parameter"].get_param(
                "project_api_url"),
            "api_key": self.env["ir.config_parameter"].get_param(
                "project_api_key"),
        }
        if not res["url"] or not res["api_key"]:
            res = False
        return res

    @api.model
    def _call_odoo(self, method, params):
        url_key = self.get_url_key()
        url = "{}/project-api/task/{}".format(url_key["url"], method)
        headers = {"API-KEY": url_key["api_key"]}
        try:
            res = requests.post(url, headers=headers, json=params)
        except Exception as e:
            _logger.error("Error when calling odoo %s", e)
            raise UserError(ERROR_MESSAGE)
        data = res.json()
        if isinstance(data, dict) and data.get("code", 0) >= 400:
            technical_info = """\n\n\n\nError Support API %s : %s : %s""" % (
                data.get("code"),
                data.get("name"),
                data.get("description")),
            _logger.error(technical_info)
            raise UserError(ERROR_MESSAGE + technical_info[0])
        return data

    def _get_support_partner_vals(self, support_uid):
        vals = self._call_odoo("read_support_author", {"uid": support_uid})
        return {
            "name": vals["name"],
            "support_last_update_date": vals["update_date"],
            "image": vals["image"],
            "support_uid": vals["uid"],
            "parent_id": self.env.ref("project_api_client.support_team").id,
        }

    def _get_support_partner(self, data):
        """ This method will return the partner info in the client database
        If the partner is missing it will be created
        If the partner information are obsolete their will be updated"""
        partner = self.env["res.partner"].search(
            [("support_uid", "=", str(data["uid"]))]
        )
        vals = self._get_support_partner_vals(data["uid"])
        if not partner:
            partner = self.env["res.partner"].create(vals)
        elif partner.support_last_update_date.strftime("%Y-%m-%d %H:%M:%S") < \
                data["update_date"]:
            partner.write(vals)
        return partner

    def _map_partner_data_to_id(self, data):
        if not data:
            return False
        elif data["type"] in ("customer", "anonymous"):
            return data["vals"]
        else:
            partner = self._get_support_partner(data)
            return (partner.id, partner.name)

    @api.model
    def create(self, vals):
        vals = self._add_missing_default_values(vals)
        vals["author"] = self._get_author_info()
        if not vals.get("model_reference", False):
            vals["model_reference"] = ""
        task_id = self._call_odoo("create", vals)
        return self.browse(task_id)

    @api.multi
    def write(self, vals):
        params = {
            "ids": self.ids,
            "vals": vals,
            "author": self._get_author_info(),
        }
        if vals.get("assignee_id"):
            partner = self.env["res.partner"].browse(vals["assignee_id"])
            if not partner.user_ids:
                raise UserError(_("You can only assign ticket to your users"))
            else:
                params["assignee"] = self._get_partner_info(partner)
        return self._call_odoo("write", params)

    @api.multi
    def unlink(self):
        return True

    @api.multi
    def copy(self, default):
        return self

    @api.multi
    def read(self, fields=None, load="_classic_read"):
        tasks = self._call_odoo(
            "read", {"ids": self.ids, "fields": fields, "load": load}
        )
        for task in tasks:
            if "author_id" in fields:
                task["author_id"] = self._map_partner_data_to_id(
                    task["author_id"]
                )
            if "assignee_id" in fields:
                task["assignee_id"] = self._map_partner_data_to_id(
                    task["assignee_id"]
                )
        return tasks

    @api.model
    def search(self, domain, offset=0, limit=0, order=None, count=False):
        result = self._call_odoo(
            "search",
            {
                "domain": domain,
                "offset": offset,
                "limit": limit,
                "order": order or "",
                "count": count,
            },
        )
        if count:
            return result
        else:
            return self.browse(result)

    @api.model
    def read_group(
        self,
        domain,
        fields,
        groupby,
        offset=0,
        limit=None,
        orderby=False,
        lazy=True,
    ):
        return self._call_odoo(
            "read_group",
            {
                "domain": domain,
                "fields": fields,
                "groupby": groupby or [],
                "offset": offset,
                "limit": limit,
                "orderby": orderby or "",
                "lazy": lazy,
            },
        )

    @api.multi
    def message_get_suggested_recipients(self):
        result = {task.id: [] for task in self}
        return result

    def _get_author_info(self):
        return self._get_partner_info(self.env.user.partner_id)

    def _get_partner_info(self, partner):
        return {
            "uid": partner.id,
            "name": partner.name,
            "image": partner.image_small,
            "email": partner.email or "",
            "mobile": partner.mobile or "",
            "phone": partner.phone or "",
        }

    @api.multi
    def message_post(self, body="", **kwargs):
        mid = self._call_odoo(
            "message_post",
            {"_id": self.id, "body": body, "author": self._get_author_info()},
        )
        return "external/%s" % mid

    @api.model
    def message_get(self, external_ids):
        messages = self._call_odoo("message_format", {"ids": external_ids})
        for message in messages:
            if "author_id" in message:
                message["author_id"] = self._map_partner_data_to_id(
                    message["author_id"]
                )
        return messages

    def fields_view_get(
        self, view_id=None, view_type=False, toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        doc = etree.XML(res["arch"])
        if view_type == "form":
            for node in doc.xpath("//field[@name='message_ids']"):
                options = safe_eval(node.get("options", "{}"))
                options.update({"display_log_button": False})
                node.set("options", repr(options))
        elif view_type == "search":
            node = doc.xpath("//search")[0]
            for project_id, project_name in self._get_select_project():
                elem = etree.Element(
                    "filter",
                    string=project_name or " ",
                    name="project_%s" % project_id,
                    domain="[('project_id', '=', %s)]" % project_id,
                )
                node.append(elem)
            node = doc.xpath("//filter[@name='my_task']")
            if node:
                node[0].attrib["domain"] = (
                    "[('assignee_id.customer_uid', '=', %s)]"
                    % self.env.user.partner_id.id
                )
        res["arch"] = etree.tostring(doc, pretty_print=True)
        return res

    @api.model
    def default_get(self, fields):
        vals = super().default_get(fields)
        if "from_model" in self._context and "from_id" in self._context:
            vals["model_reference"] = "{},{}".format(
                self._context["from_model"], self._context["from_id"]
            )
        if "from_action" in self._context:
            vals["action_id"] = self._context["from_action"]
        return vals

    def message_partner_info_from_emails(self, emails, link_mail=False):
        return []


class ExternalMessage(models.Model):
    _name = "external.message"
    _description = "External message"

    res_id = fields.Many2one(comodel_name="external.task")


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.multi
    def message_format(self):
        ids = self.ids
        if ids and isinstance(ids[0], str) and "external" in ids[0]:
            external_ids = [int(mid.replace("external/", "")) for mid in ids]
            return self.env["external.task"].message_get(external_ids)
        else:
            return super().message_format()

    @api.multi
    def set_message_done(self):
        for _id in self.ids:
            if isinstance(_id, str) and "external" in _id:
                return True
        else:
            return super().set_message_done()


class IrActionActWindows(models.Model):
    _inherit = "ir.actions.act_window"

    def _set_origin_in_context(self, action):
        context = {"default_origin_db": self._cr.dbname}
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        action_id = self._context.get("params", {}).get("action")
        _id = self._context.get("active_id")
        model = self._context.get("active_model")
        if _id and model:
            record = self.env[model].browse(_id)
            context["default_origin_name"] = record.display_name
            context["default_origin_model"] = model
        if action_id and _id:
            path = urllib.urlencode(
                {"view_type": "form", "action_id": action_id, "id": _id}
            )
            context["default_origin_url"] = "{}#{}".format(base_url, path)
        action["context"] = context

    def _set_default_project(self, action):
        # we add a try/except to avoid raising a pop-up want odoo server
        # is down
        try:
            projects = self.env["external.task"]._get_select_project()
            if projects:
                key = "search_default_project_%s" % projects[0][0]
                action["context"] = {key: 1}
        except Exception:
            _logger.warning("Fail to add the default project")

    @api.model
    def _update_action4helpdesk(self, action):
        act_ext_task = self.env.ref(
            "project_api_client.action_view_external_task")
        act_sup = self.env.ref("project_api_client.action_helpdesk")
        if act_ext_task.id == action["id"]:
            # No need to add a dynamic action because it's the dynamic act
            return False
        account = self.env["external.task"].get_url_key()
        if not account:
            # We haven't got a connection to master ERP
            return False
        # if act_sup.id == action["id"]:
        #     self._set_origin_in_context(action)
        act_helpdesk_vals = act_sup.read()[0]
        # TODO improve perf
        model = self.env["ir.model"].search(
            [("model", "=", action.get("res_model"))])
        if model:
            # act_helpdesk_vals.update(
            #     {"binding_model_id": model.id, "help": "_"})
            print(act_helpdesk_vals)
            # import pdb; pdb.set_trace()
            return False
            # return act_helpdesk_vals
        return False

        # if act_ext_task and action["id"] == act_ext_task.id:
        #     self._set_default_project(action)

    def read(self, fields=None, load="_classic_read"):
        res = super().read(fields=fields, load=load)
        actions2add = []
        # import pdb; pdb.set_trace()
        print(len(res))
        if not self.env.context.get("install_mode"):
            for action in res:
                print(action['name'], action.get('res_model'))
                ext_task_action = self._update_action4helpdesk(action)
                # import pdb; pdb.set_trace()
        #         if ext_task_action:
        #             actions2add.append(ext_task_action)
        # res.extend(actions2add)
        return res


class ExternalAttachment(models.Model):
    _name = "external.attachment"
    _description = "External attachment"

    res_id = fields.Many2one(comodel_name="external.task")
    name = fields.Char()
    datas = fields.Binary()
    res_model = fields.Char(default="project.task")
    datas_fname = fields.Char()
    type = fields.Char()
    mimetype = fields.Char()
    color = fields.Integer("Color Index")

    @api.onchange("datas_fname")
    def _file_change(self):
        if self.datas_fname:
            self.name = self.datas_fname

    @api.multi
    def read(self, fields=None, load="_classic_read"):
        tasks = self._call_odoo(
            "read", {"ids": self.ids, "fields": fields, "load": load}
        )
        return tasks

    @api.model
    def _call_odoo(self, method, params):
        url_key = self.env["external.task"].get_url_key()
        url = "{}/project-api/attachment/{}".format(url_key["url"], method)
        headers = {"API-KEY": url_key["api_key"]}
        try:
            res = requests.post(url, headers=headers, json=params)
        except Exception as e:
            _logger.error("Error when calling odoo %s", e)
            raise UserError(ERROR_MESSAGE)
        data = res.json()
        if isinstance(data, dict) and data.get("code", 0) >= 400:
            _logger.error(
                "Error Support API : %s : %s",
                data.get("name"),
                data.get("description"),
            )
            raise UserError(ERROR_MESSAGE)
        return data
