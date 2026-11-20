/* Copyright 2026 Akretion (https://www.akretion.com).
 * @author Kévin Roche <kevin.roche@akretion.com>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Component, onWillStart, useState} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class SprintDashboard extends Component {
    static template = "project_sprint_dashboard.SprintDashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.buckets = [
            {key: "done", label: _t("Done")},
            {key: "in_progress", label: _t("In progress")},
            {key: "todo", label: _t("To start")},
            {
                key: "carried_over",
                label: _t("Carried over"),
                help: _t(
                    "Tasks of the sprint coming from a previous sprint, also counted in their status"
                ),
            },
        ];
        this.statusBuckets = this.buckets.slice(0, 3);
        this.state = useState({
            data: false,
            partnerId: this.props.action.params?.partner_id || false,
            sprintId: false,
        });
        onWillStart(() => this.load());
    }

    async load() {
        const data = await this.orm.call(
            "project.sprint",
            "get_sprint_dashboard_data",
            [],
            {partner_id: this.state.partnerId, sprint_id: this.state.sprintId}
        );
        this.state.data = data;
        this.state.partnerId = data.partner_id;
        this.state.sprintId = data.sprint ? data.sprint.id : false;
    }

    onPartnerChange(ev) {
        this.state.partnerId = parseInt(ev.target.value, 10);
        this.load();
    }

    goToSprint(sprintId) {
        this.state.sprintId = sprintId;
        this.load();
    }

    goToCurrent() {
        this.state.sprintId = false;
        this.load();
    }

    openTasks(taskIds, title) {
        if (!taskIds.length) {
            return;
        }
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: title,
            res_model: "project.task",
            domain: [["id", "in", taskIds]],
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ],
            context: {group_by: ["project_id"]},
        });
    }

    openRun(taskIds, name) {
        this.openTasks(taskIds, name ? `${name} / ${_t("Run")}` : _t("Run"));
    }

    allTaskIds(buckets) {
        return this.statusBuckets.flatMap((bucket) => buckets[bucket.key].task_ids);
    }

    formatDays(days) {
        return (Math.round(days * 10) / 10).toLocaleString();
    }

    donePercent(buckets) {
        const total = this.statusBuckets.reduce(
            (sum, bucket) => sum + buckets[bucket.key].count,
            0
        );
        return total ? Math.round((buckets.done.count / total) * 100) : 0;
    }

    runPercent(buckets) {
        const days = ["done", "in_progress", "todo"].reduce(
            (sum, key) => sum + buckets[key].days,
            0
        );
        return days ? Math.round((buckets.run.days / days) * 100) : 0;
    }

    runTitle(hist) {
        return `${_t("Run")}: ${this.formatDays(hist.run_days)} / ${this.formatDays(
            hist.done_days
        )} ${_t("d")}`;
    }

    get sprintProgress() {
        const sprint = this.state.data.sprint;
        return Math.round((sprint.elapsed / sprint.duration) * 100);
    }

    get historyMax() {
        return Math.max(1, ...this.state.data.history.map((h) => h.planned_days));
    }

    historyHeight(days) {
        return Math.round((days / this.historyMax) * 100);
    }
}

registry
    .category("actions")
    .add("project_sprint_dashboard.sprint_dashboard", SprintDashboard);
