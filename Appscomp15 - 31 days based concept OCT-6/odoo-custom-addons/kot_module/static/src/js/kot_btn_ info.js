odoo.define('kot_module.Kot_Screen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');

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
        }
        Kot_Screen.template = 'Kot_Screen';
        return Kot_Screen;
    };

    Registries.Component.addByExtending(Kot_Screen, ReceiptScreen);

    return Kot_Screen;
});
