# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.http import Controller, request, route


class ExternalTaskController(Controller):

    @route(
        '/externaltask/task',
        methods=['GET', 'POST', 'PUT'],
        auth="externaltask")
    def task_list(self, **params):
        method = request.httprequest.method
        service = request.env['task.service']
        service.project = request.project
        if method == 'GET':
            submethod = params['method']
            del params['method']
            if submethod == 'read':
                res = service.get(params)
            elif submethod == 'search':
                res = service.list(params)
            elif submethod == 'read_group':
                res = service.read_group(params)
        elif method == 'POST':
            res = service.create(params)
        elif method == 'PUT':
            res = service.update(params)
        return request.make_response(res)

    @route(
        '/externaltask/message', methods=['GET', 'POST'], auth="externaltask")
    def message_list(self, **params):
        method = request.httprequest.method
        service = request.env['task.service']
        service.project = request.project
        if method == 'GET':
            res = service.get_message(params)
        elif method == 'POST':
            res = service.create_message(params)
        return request.make_response(res)
