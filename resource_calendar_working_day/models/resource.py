# -*- encoding: utf-8 -*-
# Copyright (C) 2015 AKRETION (<http://www.akretion.com>).

from datetime import datetime, timedelta

from dateutil import rrule
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    @api.multi
    def get_next_working_date(self, start_date, delay, resource_id=False):
        """First date after a delay from the start date.

        Considering the working time attached to the company calendar.
        If the current day has started or not is not relevent:
            1 day from 0:00 (start of day) = 1 day from 23:59 (end of day)
            ex: Mon 23:59 + 1 day = Tuesday 23:59
            ex: Mon 12:30 + 1 day = Tuesday 12:30

        @params start_date datetime object
        @params delay: int
        @return datetime
        """
        self.ensure_one()

        dt_leave = self.get_leave_intervals(
            resource_id, start_datetime=None, end_datetime=None
        )
        worked_days = [day["dayofweek"] for day in self.attendance_ids]
        if delay < 0:
            delta = -1
        else:
            delta = 1
        while (
            datetime.strftime(start_date, DEFAULT_SERVER_DATE_FORMAT)
            in dt_leave
            or str(start_date.weekday()) not in worked_days
        ):
            start_date = start_date + timedelta(days=delta)
        date = start_date
        while delay:
            date = date + timedelta(days=delta)
            if (
                datetime.strftime(date, DEFAULT_SERVER_DATE_FORMAT)
                not in dt_leave
                and str(date.weekday()) in worked_days
            ):
                delay = delay - delta
        return date

    @api.multi
    def get_working_days(
        self,
        start_dt,
        end_dt,
        compute_leaves=False,
        resource_id=None,
        default_interval=None,
    ):
        """Number of working days between two dates included.
        Don't care if start/end is within workhours
        ex: Monday 8am to Wednesday 22PM -> (Mon+Tue+Wed = 3days)

        @return int number of days"""
        self.ensure_one()
        days = 0
        for day in rrule.rrule(
            rrule.DAILY,
            dtstart=start_dt,
            until=end_dt,
            byweekday=self.get_weekdays(),
        ):
            day_start_dt = day.replace(hour=0, minute=0, second=0)
            if start_dt and day.date() == start_dt.date():
                # first day
                day_start_dt = start_dt
            day_end_dt = day.replace(hour=23, minute=59, second=59)
            if end_dt and day.date() == end_dt.date():
                # last day
                day_end_dt = end_dt

            ret = self.get_working_hours_of_date(
                start_dt=day_start_dt,
                end_dt=day_end_dt,
                compute_leaves=compute_leaves,
                resource_id=resource_id,
                default_interval=default_interval,
            )
            if ret:
                days += 1
        return days
