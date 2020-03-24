odoo.define('proxy_action.proxy_view', function(require) {
    'use strict';
    var ActionManager = require('web.ActionManager');
    var core = require('web.core')
    var _t = core._t

    ActionManager.include({

        _handleAction: function(action, options) {
            if (action.type == 'ir.actions.act_proxy') {
                return this._executeProxyAction(action, options);
            }
            return this._super.apply(this, arguments);
        },

        _executeProxyAction: function(action, options) {
            var self = this;
            self.do_notify(_t('Proxy action executing'), _t('Your action is being executed'));
            var action_success = true;

            $.when(_.map(action.action_list, function(task, idx) {
                $.ajax({
                    url: task['url'],
                    type: 'POST',
                    data: JSON.stringify(task['params']),
                    contentType: 'application/json',
                }).done(function(result) {
                    console.log('Proxy action sent with success: ', result);
                    return true;
                }).fail(function(result) {
                    console.log('Proxy action has failed: ', result);
                    self.do_warn(_t("Failure"), _t("Proxy action failure. Please check logs."));
                    return false;
                })
            })).then(function(requests) {
                var notif = requests.reduce(function(success, request) {
                    if (request != true) {
                        success = false;
                    }
                    return success;
                }, true);
                console.log(notif);
            });
            action = {
                type: 'ir.actions.act_window_close'
            };
            return self.doAction(action, []);
        },
    });

});