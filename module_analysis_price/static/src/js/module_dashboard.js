odoo.define("module_analysis_price.dashboard", function (require) {
    "use strict";

    /**
     * This file defines the Module Dashboard view (alongside its renderer, model
     * and controller). This Dashboard is added to the top of kanban Module
     * views, it extends both views with essentially the same code except for
     * _onDashboardActionClicked function so we can apply filters without changing our
     * current view.
     */

    var core = require("web.core");
    var KanbanController = require("web.KanbanController");
    var KanbanModel = require("web.KanbanModel");
    var KanbanRenderer = require("web.KanbanRenderer");
    var KanbanView = require("web.KanbanView");
    var SampleServer = require("web.SampleServer");
    var view_registry = require("web.view_registry");
    const session = require("web.session");

    var QWeb = core.qweb;

    // Add mock of method 'retrieve_dashboard' in SampleServer, so that we can have
    // the sample data in empty module kanban view
    let dashboardValues;
    SampleServer.mockRegistry.add("ir.module.module/retrieve_dashboard", () => {
        return Object.assign({}, dashboardValues);
    });

    // --------------------------------------------------------------------------
    // Kanban View
    // --------------------------------------------------------------------------

    var ModuleKanbanDashboardRenderer = KanbanRenderer.extend({
        events: _.extend({}, KanbanRenderer.prototype.events, {
            "click .o_dashboard_action": "_onDashboardActionClicked",
        }),
        /**
         * @override
         * @private
         * @returns {Promise}
         */
        _render: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var values = self.state.dashboardValues;
                var module_dashboard = QWeb.render(
                    "module_analysis_price.ModuleDashboard",
                    {
                        values: values,
                    }
                );
                self.$el.parent().find(".o_module_dashboard").remove();
                self.$el.before(module_dashboard);
            });
        },

        /**
         * @private
         * @param {MouseEvent}
         */
        _onDashboardActionClicked: function (e) {
            e.preventDefault();
            var $action = $(e.currentTarget);
            this.trigger_up("dashboard_open_action", {
                action_name: "module_analysis_price.module_action_dashboard_kanban",
                action_context: $action.attr("context"),
            });
        },
    });

    var ModuleKanbanDashboardModel = KanbanModel.extend({
        /**
         * @override
         */
        init: function () {
            this.dashboardValues = {};
            this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        __get: function (localID) {
            var result = this._super.apply(this, arguments);
            if (_.isObject(result)) {
                result.dashboardValues = this.dashboardValues[localID];
            }
            return result;
        },
        /**
         * @override
         * @returns {Promise}
         */
        __load: function () {
            return this._loadDashboard(this._super.apply(this, arguments));
        },
        /**
         * @override
         * @returns {Promise}
         */
        __reload: function () {
            return this._loadDashboard(this._super.apply(this, arguments));
        },

        /**
         * @private
         * @param {Promise} super_def a promise that resolves with a dataPoint id
         * @returns {Promise -> string} resolves to the dataPoint id
         */
        _loadDashboard: function (super_def) {
            var self = this;
            var dashboard_def = this._rpc({
                model: "ir.module.module",
                method: "retrieve_dashboard",
                context: session.user_context,
            });
            return Promise.all([super_def, dashboard_def]).then(function (results) {
                var id = results[0];
                dashboardValues = results[1];
                self.dashboardValues[id] = dashboardValues;
                return id;
            });
        },
    });

    var ModuleKanbanDashboardController = KanbanController.extend({
        custom_events: _.extend({}, KanbanController.prototype.custom_events, {
            dashboard_open_action: "_onDashboardOpenAction",
        }),

        /**
         * @private
         * @param {OdooEvent} e
         */
        _onDashboardOpenAction: function (e) {
            return this.do_action(e.data.action_name, {
                additional_context: JSON.parse(e.data.action_context),
            });
        },
    });

    var ModuleKanbanDashboardView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Model: ModuleKanbanDashboardModel,
            Renderer: ModuleKanbanDashboardRenderer,
            Controller: ModuleKanbanDashboardController,
        }),
    });

    view_registry.add("module_kanban_dashboard", ModuleKanbanDashboardView);

    return {
        ModuleKanbanDashboardModel: ModuleKanbanDashboardModel,
        ModuleKanbanDashboardRenderer: ModuleKanbanDashboardRenderer,
        ModuleKanbanDashboardController: ModuleKanbanDashboardController,
    };
});
