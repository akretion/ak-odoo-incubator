/** @odoo-module **/

import {registry} from "@web/core/registry";

async function executeProxyAction({env, action}) {
    action.action_list.map(function (act) {
        let msg = env._t("Your action is being executed");
        if (act.params.args && act.params.args[2] !== undefined) {
            msg = act.params.args[2];
        }
        env.services.notification.add(msg, {
            type: "info",
        });
        $.ajax({
            url: act.url,
            type: "POST",
            data: JSON.stringify(act.params),
            contentType: "application/json",
        }).fail(function (result) {
            console.log("Proxy action has failed: ", result);
            env.services.notification.add(
                env._t("Proxy action failure. Please check logs."),
                {type: "danger"}
            );
            return result;
        });
    });
    var act_close = {
        type: "ir.actions.act_window_close",
    };
    return env.services.action.doAction(act_close, []);
}

registry.category("action_handlers").add("ir.actions.act_proxy", executeProxyAction);
