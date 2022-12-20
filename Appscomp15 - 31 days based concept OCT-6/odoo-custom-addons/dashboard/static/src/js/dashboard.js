
console.log("gggggggggggggggggggggggggggggggggggggggg")
odoo.define('dashboard.dashboard_kanban', function (require) {
    "use strict";

//    const { useState } = owl.hooks;
//    const models = require('point_of_sale.models');
//    var Registries = require('point_of_sale.Registries');

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session = require('web.session');
    var QWeb = core.qweb;

    var Dialog = require('web.Dialog');

    var DashboardKanban = AbstractAction.extend({
        template: 'dashboard_template',
        events:{},
        wait: true,

        init: function(parent, action) {
            this._super(parent, action);
        },

        start: function() {
            var self = this;
            setInterval(function() {
                self.load_data();
            }, 5000);
        },

        load_data: function () {
            var self = this;
            if ($('.dashboard_container').length === 0) {
                self.$('.kanban_view').html(QWeb.render('dashboard_data', {}));
            }
            self._rpc({
                model: 'medical.patient',
                method: 'get_patient_values',
                args: [[]],
            }).then(function(data) {
            if (self.wait) {
                self.wait_one_hours(data,);
            }
            if (self.wait) {
                self.wait_two_hours(data,);
            }
            if (self.wait) {
                self.wait_three_hours(data,);
            }
            });

        },
        wait_one_hours: function(data) {
            var self = this;
            const not_register = data.filter((o) => o.time=== '1');
            this.$('.kitchen_grid.pending .pending_content').html(QWeb.render('dashboard_data', {
                orders: not_register
            }));
        },

        wait_two_hours: function(data) {
            var self = this;
            const register = data.filter((o) => o.time === '2');
            this.$('.kitchen_grid.prepare .preparing_content').html(QWeb.render('dashboard_data', {
                orders: register
            }));
        },

        wait_three_hours: function(data,) {
            var self = this;
            const visit = data.filter((o) => o.time === '3');
            this.$('.kitchen_grid.done .done_content').html(QWeb.render('dashboard_data', {
                orders: visit
            }));
        },

    });

    core.action_registry.add("dashboard_kanban", DashboardKanban);
});