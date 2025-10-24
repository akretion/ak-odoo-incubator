/** @odoo-module **/
// Copyright 2025 Akretion (http://www.akretion.com).
// @author Florian Mounier <florian.mounier@akretion.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import {Many2ManyTagsField} from "@web/views/fields/many2many_tags/many2many_tags_field";
import {Many2XAutocomplete} from "@web/views/fields/relational_utils";
import {MergeRequestsList} from "./merge_requests_list.esm";
import {registry} from "@web/core/registry";

export class Many2ManyMergeRequestsField extends Many2ManyTagsField {
    getMergeRequestProps(record) {
        return {
            id: record.id,
            resId: record.resId,
            text: `${record.data.project_path}!${record.data.gitlab_iid}`,
            tooltip: `${record.data.project_namespace} / ${record.data.project_name}
${record.data.name}

${record.data.description}`,
            draft: record.data.draft,
            state: record.data.state,
            onClick: (ev) => this.onMergeRequestClick(ev, record),
            onDelete: this.props.readonly ? undefined : () => this.deleteTag(record.id),
            onKeydown: this.onTagKeydown.bind(this),
        };
    }

    onMergeRequestClick(ev, record) {
        ev.preventDefault();
        ev.stopPropagation();
        const url = record.data.web_url;
        if (url) {
            window.open(url, "_blank");
        }
    }

    get mrs() {
        return this.props.value.records.map((record) =>
            this.getMergeRequestProps(record)
        );
    }
}
Many2ManyMergeRequestsField.fieldsToFetch = {
    project_path: {name: "project_path", type: "char"},
    project_namespace: {name: "project_namespace", type: "char"},
    project_name: {name: "project_name", type: "char"},
    name: {name: "name", type: "char"},
    description: {name: "description", type: "text"},
    gitlab_iid: {name: "gitlab_iid", type: "integer"},
    state: {name: "state", type: "selection"},
    draft: {name: "draft", type: "boolean"},
    web_url: {name: "web_url", type: "char"},
};
Many2ManyMergeRequestsField.template = "gitlab_integration.Many2ManyMergeRequestsField";
Many2ManyMergeRequestsField.components = {
    Many2XAutocomplete,
    MergeRequestsList,
};

registry
    .category("fields")
    .add("many2many_merge_requests", Many2ManyMergeRequestsField);
