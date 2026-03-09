# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import format_date

MAX_SPRINT_DEPTH = 4

SOW = 1
EOW = 5


def middle_date(date_start, date_end):
    return date_start + (date_end - date_start) / 2


class ProjectSprint(models.Model):
    _name = "project.sprint"
    _description = "Project Sprint"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "full_name"
    _order = "date_start, level"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    full_name = fields.Char(compute="_compute_full_name", store=True)

    parent_id = fields.Many2one("project.sprint", string="Parent Sprint", index=True)
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many("project.sprint", "parent_id", string="Child Sprints")
    child_count = fields.Integer(compute="_compute_child_count")
    level = fields.Integer(compute="_compute_level", store=True, recursive=True)
    max_level = fields.Boolean(compute="_compute_max_level")

    date_start = fields.Date()
    date_end = fields.Date()

    @api.constrains("date_start", "date_end")
    def _check_date(self):
        for record in self:
            if record.date_start and record.date_end:
                if record.date_start > record.date_end:
                    raise ValidationError(
                        self.env._("The start date must be before the end date.")
                    )

    @api.constrains("parent_id")
    def _check_parent_not_circular(self):
        if not self._check_recursion():
            raise ValidationError(self.env._("You cannot create recursive sprint."))

    @api.depends("parent_id.level")
    def _compute_level(self):
        for record in self:
            record.level = record.parent_id.level + 1 if record.parent_id else 1

    @api.depends("level")
    def _compute_max_level(self):
        for record in self:
            record.max_level = record.level == MAX_SPRINT_DEPTH

    @api.depends("name", "parent_id.name")
    def _compute_full_name(self):
        for record in self:
            record.full_name = (
                f"{record.parent_id.full_name}/{record.name}"
                if record.parent_id
                else record.name
            )

    @api.depends("child_ids")
    def _compute_child_count(self):
        data = self.read_group(
            [("parent_id", "in", self.ids)], ["parent_id"], ["parent_id"]
        )
        mapped_data = {m["parent_id"][0]: m["parent_id_count"] for m in data}
        for record in self:
            record.child_count = mapped_data.get(record.id, 0)

    def _get_dow_from_date(self, date_, dow):
        cal = date_.isocalendar()
        return date.fromisocalendar(cal.year, cal.week, dow)

    def _generate_quarters(self):
        children = self.child_ids

        year = middle_date(self.date_start, self.date_end).year
        quarter = 0
        while True:
            start = date.fromisocalendar(year, 1 + quarter * 13, SOW)
            end = date.fromisocalendar(year, (quarter + 1) * 13, EOW)
            if quarter == 3:
                # In case the year has 53 weeks:
                try:
                    end = date.fromisocalendar(year, (quarter + 1) * 13 + 1, EOW)
                except ValueError:  # pylint: disable=except-pass
                    pass

            prefix = self.env._("Q")
            sprint_name = f"{prefix}{quarter + 1}"
            quarter += 1
            if quarter == 4:
                quarter = 0
                year += 1

            if end < self.date_start:
                continue
            if start > self.date_end:
                break

            sprint = children.filtered(
                lambda x, sprint_name=sprint_name: x.name == sprint_name
            )
            if not sprint:
                children |= self.create(
                    {
                        "name": sprint_name,
                        "parent_id": self.id,
                        "date_start": max(start, self.date_start),
                        "date_end": min(end, self.date_end),
                    }
                )
        return children

    def _generate_months(self):
        children = self.child_ids

        year = middle_date(self.date_start, self.date_end).year
        month = self._get_dow_from_date(self.date_start, 7).month
        while True:
            start = self._get_dow_from_date(date(year, month, 5), SOW)
            end = self._get_dow_from_date(date(year, month, 28), EOW)
            sprint_name = format_date(
                self.env, middle_date(start, end), date_format="MMMM"
            ).title()

            month += 1
            if month > 12:
                month = 1
                year += 1

            if end < self.date_start:
                continue
            if start > self.date_end:
                break

            sprint = children.filtered(
                lambda x, sprint_name=sprint_name: x.name == sprint_name
            )
            if not sprint:
                children |= self.create(
                    {
                        "name": sprint_name,
                        "parent_id": self.id,
                        "date_start": max(start, self.date_start),
                        "date_end": min(end, self.date_end),
                    }
                )
        return children

    def _generate_fortnights(self):
        children = self.child_ids

        year = middle_date(self.date_start, self.date_end).year
        week = self.date_start.isocalendar()[1]
        while True:
            start = date.fromisocalendar(year, week, SOW)
            end = date.fromisocalendar(year, week + 1, EOW)
            if week == 51:
                # In case the year has 53 weeks:
                try:
                    end = date.fromisocalendar(year, 53, EOW)
                except ValueError:  # pylint: disable=except-pass
                    pass
            month_fortnight = middle_date(start, end).day // 15
            prefix = self.env._("F")
            sprint_name = f"{prefix}{month_fortnight + 1}"

            week += 2
            if week > 51:
                week = 1
                year += 1

            if end < self.date_start:
                continue
            if start > self.date_end:
                break

            sprint = children.filtered(
                lambda x, sprint_name=sprint_name: x.name == sprint_name
            )
            if not sprint:
                children |= self.create(
                    {
                        "name": sprint_name,
                        "parent_id": self.id,
                        "date_start": max(start, self.date_start),
                        "date_end": min(end, self.date_end),
                    }
                )
        return children

    def _generate_sprints(self):
        self.ensure_one()

        if self.level == 1:
            if not self.name.isdigit():
                raise ValidationError(
                    self.env._("The name of the top level sprint must be a year.")
                )
            if not self.date_start:
                self.date_start = date.fromisocalendar(int(self.name), 1, SOW)

            if not self.date_end:
                self.date_end = date.fromisocalendar(
                    int(self.name) + 1, 1, 5
                ) - timedelta(weeks=1)

        if not self.date_start or not self.date_end:
            raise ValidationError(self.env._("The start and end date are required."))

        if self.level == 4:
            return

        children = [
            self._generate_quarters,
            self._generate_months,
            self._generate_fortnights,
        ][self.level - 1]()

        children.action_generate()

    def action_generate(self):
        for rec in self:
            rec._generate_sprints()
