'use strict';
odoo.define('proxy_action.proxy_view', function (require) {
    var ActionManager = require('web.ActionManager');
    var core = require('web.core')
    var _t = core._t
    ActionManager.include({
        ir_actions_act_proxy: function (action, options) {
            var self = this;
            self.do_notify(_t('Proxy action executing'), _t('Your action is being executed'));

            var action_success = true;
            action.action_list.forEach(function (task) {
                $.ajax({
                    url: task['url'],
                    type: 'POST',
                    data: JSON.stringify(task['params']),
                    contentType: 'application/json',
                    async: false,
                }).done(function (result) {
                    console.log("Individual proxy action has been successfully sent: ", result);
                }).fail(function (result) {
                    console.log('Individual proxy action has failed: ', result);
                    action_success = false;
                })
            })
            if (action_success === true){
                self.do_notify(_t('Success'), _t('Proxy action successfully sent.'));
            }
            else{
                self.do_warn(_t("Failure"), _t("Proxy action failure. Please check logs."));
            }

            this.do_action({"type": "ir.actions.act_window_close"});
        }
    });
});
