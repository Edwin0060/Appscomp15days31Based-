odoo.define('waiter_pos.WaiterNameSelectionBtn', function(require) {
'use strict';
    const { Gui } = require('point_of_sale.Gui');
    const PosComponent = require('point_of_sale.PosComponent');
    const { posbus } = require('point_of_sale.utils');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    var rpc = require('web.rpc');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var QWeb = core.qweb;
    var models = require('point_of_sale.models');

    models.load_models({
        model: 'hr.employee',
        fields: ['id', 'name'],
        domain: function(){ return [['is_a_waiter','=',true]]; },
        loaded: function (self, employee) {
            self.employee_name_by_id = {};
            for (var i = 0; i < employee.length; i++) {
                self.employee_name_by_id[employee[i].id] = employee[i];
            }
        }
    });

    class WaiterNameSelectionBtn extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        is_available() {
            const order = this.env.pos.get_order();
            return order
        }

        async onClick() {
            var order = this.env.pos.get_order();
            if (order.get_orderlines().length > 0) {
                const waiter = [ { } ];
                let values = this.env.pos.employee_name_by_id
                console.log(this.env.pos.employee_name_by_id)
                if (values) {
			       _.each(values, function(values){
				       waiter.push({
					       id: values.id,
					       label: values.name,
					       item: values,
				       });
			       });
		       }
               const { confirmed, payload: selectedWaiter } =await this.showPopup("SelectionPopup", {
			       title: 'Select Waiter',
			       list: waiter,
		       });
		       if (confirmed) {
			      console.log("000000000000000000000000000000000000000000000",selectedWaiter.name)
			      var infos = {
                      'ni_customer_contact':selectedWaiter.name,
                  };
                  var waiter_details = {
                      'name':selectedWaiter.name,
                      'id':selectedWaiter.id,
                      'order_id':this.env.pos.get_order_with_uid(),
                  };
//                  this.showScreen('FloorScreen');
                  this.rpc({
                    model: 'pos.order',
                    method: 'save_waiter',
                    args: [[], waiter_details],
                    })
                  console.log("GGGGGGGGGGGGGggg",waiter_details)
                  this.env.pos.get_order().add_client_detail(infos);
		       }
            } else {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Nothing to Order'),
                    body: this.env._t('Please select any Order'),
                });
            }
        }


   }

    WaiterNameSelectionBtn.template = 'WaiterNameSelectionBtn';
    ProductScreen.addControlButton({
        component: WaiterNameSelectionBtn,
        condition: function() {
            return this.env.pos.config.waiter_configuration;
        },
   });
    Registries.Component.add(WaiterNameSelectionBtn);
    return WaiterNameSelectionBtn;
});