/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

async function executeProxyAction ({ env, action }) {
    let error = false;
    for (const act of action.action_list) {

        let msg = _t("Your action is being executed");
        // The arg act.params.args[2] can contain a custom message to display for user
        // (ex used printer name)
        const { args } = act.params;
        if (
            args &&
            args.length >= 2 &&
            args[2]?.length
        ) {
            msg = act.params.args[2];
        }
        env.services.notification.add(msg, {
            type: "info",
        });

        try {
            const response = await fetch(act.url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(act.params)
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
        } catch (error) {
            console.log("Proxy action has failed: ", error);
            env.services.notification.add(
                _t("Proxy action failure. Please check logs."),
                { type: "danger" }
            );
            error = true;
        }

    }
    if (!error) {
        var act_close = {
            type: "ir.actions.act_window_close",
        };
        return env.services.action.doAction(act_close, []);
    }

}

registry.category("action_handlers").add("ir.actions.act_proxy", executeProxyAction);
