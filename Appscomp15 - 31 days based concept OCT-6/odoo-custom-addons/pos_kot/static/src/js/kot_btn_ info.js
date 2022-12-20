odoo.define('pos_kot.Kot_Screen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const Popup = require('point_of_sale.ConfirmPopup');
    const PosComponent = require('point_of_sale.PosComponent');
    const PaymentScreen = require('point_of_sale.PaymentScreen');

    const Kot_Screen = (ReceiptScreen) => {
        class Kot_Screen extends ReceiptScreen {
            confirm() {
                this.props.resolve({ confirmed: true, payload: null });
                this.trigger('close-temp-screen');
            }
            whenClosing() {
                this.confirm();
            }
            /**
             * @override
             */
            async printReceipt() {
                await super.printReceipt();
                this.currentOrder._printed = false;
            }
            go_payment_screen() {
                this.showScreen('PaymentScreen');
                this.confirm();
            }
        }
        Kot_Screen.template = 'Kot_Screen';
        return Kot_Screen;
    };

    Registries.Component.addByExtending(Kot_Screen, ReceiptScreen);

    return Kot_Screen;
});
