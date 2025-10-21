/** @odoo-module **/
// Copyright 2025 Akretion (http://www.akretion.com).
// @author Florian Mounier <florian.mounier@akretion.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import {Component} from "@odoo/owl";

export class MergeRequestsList extends Component {
    get mrs() {
        return this.props.mrs;
    }
    get tooltipInfo() {
        return JSON.stringify({
            mrs: this.props.mrs.map((mr) => ({
                text: mr.tooltip,
                id: mr.id,
            })),
        });
    }
}
MergeRequestsList.template = "gitlab_integration.MergeRequestsList";
MergeRequestsList.defaultProps = {
    className: "",
    displayText: true,
};
MergeRequestsList.props = {
    className: {type: String, optional: true},
    displayText: {type: Boolean, optional: true},
    name: {type: String, optional: true},
    mrs: {type: Object, optional: true},
};
