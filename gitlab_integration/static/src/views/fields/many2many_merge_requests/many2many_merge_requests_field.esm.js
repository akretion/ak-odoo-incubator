// Copyright 2025 Akretion (http://www.akretion.com).
// @author Florian Mounier <florian.mounier@akretion.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import {
    Many2ManyTagsField,
    many2ManyTagsField,
} from "@web/views/fields/many2many_tags/many2many_tags_field";
import {Many2XAutocomplete} from "@web/views/fields/relational_utils";
import {MergeRequestsList} from "./merge_requests_list.esm";
import {registry} from "@web/core/registry";

export class Many2ManyMergeRequestsField extends Many2ManyTagsField {
    static template = "gitlab_integration.Many2ManyMergeRequestsField";
    static components = {
        Many2XAutocomplete,
        MergeRequestsList,
    };

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
        return this.props.record.data[this.props.name].records.map((record) =>
            this.getMergeRequestProps(record)
        );
    }
}

export const many2ManyMergeRequestsField = {
    ...many2ManyTagsField,
    component: Many2ManyMergeRequestsField,
    displayName: "MergeRequests",
    supportedTypes: ["many2many"],
    relatedFields: [
        {name: "project_path", type: "char"},
        {name: "project_namespace", type: "char"},
        {name: "project_name", type: "char"},
        {name: "name", type: "char"},
        {name: "description", type: "text"},
        {name: "gitlab_iid", type: "integer"},
        {
            name: "state",
            type: "selection",
            selection: [
                ["opened", "Opened"],
                ["closed", "Closed"],
                ["merged", "Merged"],
                ["locked", "Locked"],
            ],
        },
        {name: "draft", type: "boolean"},
        {name: "web_url", type: "char"},
    ],
};

registry
    .category("fields")
    .add("many2many_merge_requests", many2ManyMergeRequestsField);
