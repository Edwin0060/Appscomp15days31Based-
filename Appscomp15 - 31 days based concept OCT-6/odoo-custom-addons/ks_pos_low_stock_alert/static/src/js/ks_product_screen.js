/*
    @Author: KSOLVES India Private Limited
    @Email: sales@ksolves.com
*/

odoo.define('ks_pos_low_stock_alert.ks_product_screen', function (require) {
    "use strict";
    const KsProductScreen = require('point_of_sale.ProductScreen');
    const ks_utils = require('ks_pos_low_stock_alert.utils');
    const Registries = require('point_of_sale.Registries');

    const ks_product_screen = (KsProductScreen) =>
        class extends KsProductScreen {
            _onClickPay() {
                var self = this;
                var order = self.env.pos.get_order();
                if(ks_utils.ks_validate_order_items_availability(self.env.pos.get_order(), self.env.pos.config)) {
                    var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                        return line.has_valid_product_lot();
                    });
                    if(!has_valid_product_lot){
                        self.showPopup('ConfirmPopup',{
                            'title': _t('Empty Serial/Lot Number'),
                            'body':  _t('One or more product(s) required serial/lot number.'),
                            confirm: function(){
                                self.showScreen('PaymentScreen');
                            },
                        });
                    } else{
                        this.showScreen('PaymentScreen');
                    }
                }

        }
    };

    Registries.Component.extend(KsProductScreen,ks_product_screen);

    return KsProductScreen;
    });