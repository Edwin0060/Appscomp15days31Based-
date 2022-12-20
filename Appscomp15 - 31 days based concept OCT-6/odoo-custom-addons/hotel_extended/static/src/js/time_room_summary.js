odoo.define("hotel_extended.time_hotel_room_summary", function (require) {
    "use strict";

    var core = require("web.core");
    var registry = require("web.field_registry");
    var basicFields = require("web.basic_fields");
    var FieldText = basicFields.FieldText;
    var QWeb = core.qweb;
    var FormView = require("web.FormView");
    var py = window.py;

  var MyWidget = FieldText.extend({
    className: 'o_field_text',
        events: _.extend({}, FieldText.prototype.events, {
         selector: '.o_field_text',
            'change .o_field_text': "_onFieldChanged",
        }),
        init: function () {
            this._super.apply(this, arguments);
            if (this.mode === "edit") {
                this.tagName = "span";
            }
            this.set({
                date_to: false,
                date_from: false,
                summary_header: false,
                room_summary: false,
            });
            this.set({
                summary_header: py.eval(this.recordData.summary_header),
            });
            this.set({
                room_summary: py.eval(this.recordData.room_summary),
            });
        },
        start: function () {
            var self = this;
            if (self.setting) {
                return;
            }
            if (!this.get("summary_header") || !this.get("room_summary")) {
                return;
            }
            this.renderElement();
            this.view_loading();
        },
        initialize_field: function () {
            FormView.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:summary_header", self, self.start);
            self.on("change:room_summary", self, self.start);
        },
        view_loading: function (r) {
            return this.load_form(r);
        },

        load_form: function () {
            var self = this;
//            this.$el.find(".table_free").bind("click", function () {
//                const d = new Date();
//                var hour = d.getHours();
//                var hour_2 = hour.toString();
//                var minutes = d.getMinutes();
//                var min = minutes.toString();
//
//                var year = d.getFullYear().toString();
//                var month =d.getMonth() + 1;
//                var day = d.getDate().toString();
//
//                var d1 = d.toString();
//                var month_1 = month.toString();
//                var day_day = day.length;
//                if(day_day ==  1){
//                    var full_date = year + "-0" + month_1 + "-0" + day + " "
//                }else{
//                    var full_date = year + "-0" + month_1  + "-" + day + " "
//                }
//
//                var full_time = hour_2 + ":" + min + ":00"
//
//
//
//                console.log(full_date,"================",$(this).attr("date"),"===",$(this).attr("entry"),full_time)
//                if ($(this).attr("date") <= full_date){
//                    if ($(this).attr("entry") < full_time){
//                    console.log("=========================================", $(this).attr("entry"), typeof(hour_2))
//                    alert(
//                    "Alert-Warning!,  Dear Guest, you cannot reserve the past time, Reservation will be available from current time onwards,");
//                    }
//                    else{
//                        self.do_action({
//                            type: "ir.actions.act_window",
//                            res_model: "quick.room.reservation",
//                            views: [[false, "form"]],
//                            target: "new",
//                            context:{
//                                room_id: $(this).attr("data"),
//                                time: $(this).attr("time"),
//                                date: $(this).attr("date"),
//                                entry: $(this).attr("entry"),
//                                default_adults: 1,
//                                default_active: true,
//                                },
//                            })
//                        }
//
//                }
//                else{
//                    self.do_action({
//                        type: "ir.actions.act_window",
//                        res_model: "quick.room.reservation",
//                        views: [[false, "form"]],
//                        target: "new",
//                        context:{
//                            room_id: $(this).attr("data"),
//                            time: $(this).attr("time"),
//                            date: $(this).attr("date"),
//                            entry: $(this).attr("entry"),
//                            default_adults: 1,
//                            default_active: true,
//                        },
//                    });
//                }
//
//            });
            this.$el.find(".table_reserved").bind("click", function () {
                var res_id = $(this).data("id");
                self.do_action({
                    type: "ir.actions.act_window",
                    res_model: "hotel.reservation",
                    views: [[false, "form"]],
                    target: "new",
                    res_id: res_id || false,
                });
            });
        },
        renderElement: function () {
            this._super();
            this.$el.html(
                QWeb.render("TimeRoomSummary", {
                    widget: this,
                })
            );
        },
        _onFieldChanged: function (event) {
        console.log('Js csalledd My widgetttttttt>>>>>141414>>>>')
            this._super();
            this.lastChangeEvent = event;
            this.set({
                summary_header: py.eval(this.recordData.summary_header),
            });
            this.set({
                room_summary: py.eval(this.recordData.room_summary),
            });
            this.renderElement();
            this.view_loading();
        },
    });

    registry.add("Time_Room_Reservation", MyWidget);
    return MyWidget;
});
