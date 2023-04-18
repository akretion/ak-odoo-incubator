/** @odoo-module **/

import {registry} from "@web/core/registry";

async function executeProxyAction({env, action}) {
    action.action_list.map(function (act) {
        env.services.notification.add(env._t("Your action is being executed"), {
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
