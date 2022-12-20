odoo.define("ls_pos_stock.product_item", function(require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductList = require('point_of_sale.ProductList');

    const models = require("point_of_sale.models");
    models.load_fields("product.product", ["qty_available"]);

    const { useState } = owl.hooks;


    const ProductListNew = ProductList =>
    class extends ProductList {


        constructor() {
            super(...arguments);
            this.state = useState({
                display_stock_pos : ""
            });
        }

        async willStart() {
            const display_stock_pos = await this.env.services.rpc({
                model: 'pos.config',
                method: 'get_display_stock_pos',
                args: [[]],
            });
            this.state.display_stock_pos = display_stock_pos
        
        }
        
    }

    Registries.Component.extend(ProductList, ProductListNew);

});

