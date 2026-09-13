// Copyright 2025 Akretion (http://www.akretion.com).
// @author Florian Mounier <florian.mounier@akretion.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("auth_oauth_redirect_fix.auth_oauth_redirect_fix", function (require) {
    "use strict";
    var publicWidget = require("web.public.widget");

    publicWidget.registry.AuthOAuthRedirectFix = publicWidget.Widget.extend({
        selector: ".oe_login_form",

        _fix_oauth_redirect: function (originalUrl) {
            // Parse the original URL to get the state redirect url
            const url = URL.parse(originalUrl);
            const stateParam = url.searchParams.get("state");
            if (!stateParam) {
                return originalUrl;
            }
            const state = JSON.parse(stateParam);
            if (!state.r) {
                return originalUrl;
            }
            const redirectUrl = URL.parse(decodeURIComponent(state.r));
            // Set the current fragment
            if (!redirectUrl.hash) {
                redirectUrl.hash = window.location.hash;
            }
            state.r = encodeURIComponent(redirectUrl.toString());
            url.searchParams.set("state", JSON.stringify(state));
            return url.toString();
        },

        start: function () {
            const self = this;
            const hash = window.location.hash;
            if (hash) {
                // Process all the oauth links
                this.$el
                    .find(".o_auth_oauth_providers a.list-group-item-action")
                    .each(function () {
                        const $link = $(this);
                        try {
                            $link.attr(
                                "href",
                                self._fix_oauth_redirect($link.attr("href"), hash)
                            );
                        } catch (e) {
                            console.error("Error while fixing OAuth redirect URL", e);
                        }
                    });
            }
            return this._super.apply(this, arguments);
        },
    });
});
