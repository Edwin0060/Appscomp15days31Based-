odoo.define('pos_dashboard_ks.dashboard_kanban', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session = require('web.session');
    var QWeb = core.qweb;

    var Dialog = require('web.Dialog');

    var DashboardKanban = AbstractAction.extend({
        template: 'dashboard_template',
        events:{
            'click .start_order_line': '_onStartOrEndOrderLine',
            'click .end_order_line': '_onStartOrEndOrderLine',
            'click .print_order_line': '_onPrintOrderLine',
            'click .show_note': '_onShowNote',
            'click .bill_order':'_returnBill',
        },
        show_pending_orders: true,
        show_in_progress_orders: true,
        show_done_orders: true,
        category_ids: [],
        pos_config_ids: [],


        init: function(parent, action) {
            this._super(parent, action);
        },

        start: function() {
            var self = this;
            this._rpc({
                model: 'res.users',
                method: 'search_read',
                args: [[['id', '=', session.uid]], ['kitchen_category_ids']],
                args: [[['id', '=', session.uid]], ['kitchen_category_ids', 'pos_config_ids']],
            }).then(function (data) {
                self.category_ids = data[0].kitchen_category_ids;
                self.pos_config_ids = data[0].pos_config_ids;
                self.load_data();
            });
            setInterval(function() {
                self.load_data();
            }, 10000);
        },

        load_data: function () {
            var self = this;
            if ($('.dashboard_container').length === 0) {
                self.$('.kanban_view').html(QWeb.render('dashboard_orders', {}));
            }
            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0');
            var yyyy = today.getFullYear();

            today = yyyy + '-' + mm + '-' + dd;
            var fields = ['id', 'dashboard_state', 'name', 'start_date', 'user_id', 'pos_reference', 'table_id', 'create_date', 'customer_count'];
            self._rpc({
                model: 'pos.order.line',
                method: 'search_read',
                args: [[
                    ['create_date', '>=', today],
                    ['product_id.pos_categ_id.id', 'in', self.category_ids],
                    ['order_id.session_id.config_id.id', 'in', self.pos_config_ids]],
                    ['dashboard_state', 'full_product_name', 'qty', 'order_id', 'product_id', 'note']
                ],
            }).then(function(lines) {
                console.log('lim', lines);
                self._rpc({
                    model: 'pos.order',
                    method: 'search_read',
                    args: [[['create_date', '>=', today], ['dashboard_state', '=', ['pending', 'in_progress', 'done']]], fields],
                }).then(function(orders) {
                    orders.forEach(function(order) {
                        order.user_id = order.user_id && order.user_id.length > 0 ? order.user_id[1] : '';
                        order.table_id = order.table_id && order.table_id.length > 0 ? order.table_id[1] : '';
                        order.create_date = self.convertDateToLocale(new Date(order.create_date));
                    });
                    if (self.show_pending_orders) {
                        self.getPendingOrders(lines, orders);
                    }
                    if (self.show_in_progress_orders) {
                        self.getInProgressOrders(lines, orders);
                    }
                    if (self.show_done_orders) {
                        self.getDoneOrders(lines, orders);
                    }
                    console.log("++++++++++++++++++++++++++++++",orders)
                  
                });
               
            });

        },

        convertDateToLocale: function(date) {
            var newDate = new Date(date.getTime()+date.getTimezoneOffset()*60*1000);
            var offset = date.getTimezoneOffset() / 60;
            var hours = date.getHours();
            newDate.setHours(hours - offset);
            return newDate.toLocaleString();
        },
        getPendingOrders: function(lines, orders) {
            var self = this;
            var all_orders = this.getOrdersWithLines(orders, lines);
            orders = all_orders.filter((o) => o.dashboard_state === 'pending');
            var processing_orders = all_orders.filter((o) => o.dashboard_state === 'in_progress');
            var done_orders = all_orders.filter((o) => o. dashboard_state === 'done');

            this.$('.kitchen_grid.pending .pending_content').html(QWeb.render('dashboard_orders', {
                orders: orders
            }));
            console.log("=============",orders)

            this.$('.kitchen_grid.prepare .preparing_content').html(QWeb.render('dashboard_orders', {
                orders: processing_orders
            }));
            console.log("=====PREPARE========",processing_orders)

            this.$('.kitchen_grid.done .done_content').html(QWeb.render('dashboard_orders', {
                orders: done_orders
            }));


        },
    
        getInProgressOrders: function(lines, orders) {
            var self = this;
            orders = this.getOrdersWithLines(orders, lines);
            orders = orders.filter((order) => {
                const in_progress_lines = order.lines.filter((line) => line.dashboard_state === 'in_progress');
                const pending_lines = order.lines.filter((line) => line.dashboard_state === 'pending');
                const done_lines = order.lines.filter((line) => line.dashboard_state === 'done');
                return (in_progress_lines.length > 0) || (pending_lines.length > 0 && done_lines.length > 0);
            });
        },
    
        getDoneOrders: function(lines, orders) {
            var self = this;
            orders = this.getOrdersWithLines(orders, lines);
            orders = orders.filter((order) => {
                return order.lines.filter((line) => line.dashboard_state !== 'done').length === 0;
            });
        },
        getOrdersWithLines: function(orders, lines) {
            orders.forEach(function(order) {
                order.lines = lines.filter((line) => line.order_id[0] === order.id);
            });
            orders = orders.filter((order) => order.lines.length > 0);
            console.log("Prasathhhhhhhhhhhh1111111111hhhhhhhh", orders)
            return orders;
        },

        _onStartOrEndOrderLine: function (ev) {
            var today = new Date();
            var date = today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2, '0') + '-'+String(today.getDate()).padStart(2, '0');
            var time = String(today.getHours()).padStart(2, '0') + ":" + String(today.getMinutes()).padStart(2, '0') + ":" + String(today.getSeconds()).padStart(2, '0');
            var dateTime = date+' '+time;
            var self = this;
            ev.stopPropagation();
            var values = {}
            var id = $(ev.currentTarget).parent().data( "id");
            values[$(ev.currentTarget).data( "type") === 'start' ? 'start_date' : 'end_date'] = dateTime;

            this._rpc({
                model: 'pos.order.line',
                method: 'state_change',
                args: [[id], values],
            }).then(function () {
                self.load_data();
            });
        },
         _onShowNote: function (ev) {
            var note = $(ev.currentTarget).data( "note");
            var html_data = '<div class="icon-close-container"><div class="recipie_description">' + note + '</div>';
            html_data += '</div>';
            self.$('.note_container').html(html_data);
            self.$('.note_container').show();

        },
        load_kot: function (data) {
            console.log("333333333333333333333333333",data)
            var self = this;
            this.$el.html(QWeb.render("Kot_template", {orders: data}));
            window.print();
            history.go(0);
        },

        _onPrintOrderLine: function(ev) {
            var self = this;
            ev.stopPropagation();
            var values = {}
            var id = $(ev.currentTarget).parent().data( "id");
            console.log("============2525252=================",id)
            this._rpc({
                model: 'pos.order.line',
                method: 'kot_function',
                args: [id,id],
            }).then(function (data) {
                console.log("============1111111=================",data)
                self.load_kot(data);
            });
        },
        _returnBill: function(ev){
            var self = this;
            ev.stopPropagation();
            var values = {}
            var id = $(ev.currentTarget).parent().data( "id");
            console.log("============IDIDIDIDDIDIDDI=================",id)
            this._rpc({
                model: 'pos.order.line',
                method: 'kot_function_return',
                args: [id,id],
            }).then(function (data) {
                console.log("============rufgeuicfgeucfegcfuevo=================",data)
                self.do_action({
                    name: 'POS Order',
                    res_model: 'pos.order',
                    res_id: data,
                    views: [[false, 'form']],
                    type: 'ir.actions.act_window',
                    view_mode: 'form',
                });
            });

        }


    });

    core.action_registry.add("dashboard_kanban", DashboardKanban);
    });
