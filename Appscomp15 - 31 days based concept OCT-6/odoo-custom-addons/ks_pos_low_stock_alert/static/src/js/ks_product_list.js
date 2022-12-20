/*
    @Author: KSOLVES India Private Limited
    @Email: sales@ksolves.com
*/

odoo.define('ks_pos_low_stock_alert.ks_product_list', function (require) {
    "use strict";
    const KsProductItem = require('point_of_sale.ProductItem');
    const Registries = require('point_of_sale.Registries');

    const ks_product_item = (KsProductItem) =>
        class extends KsProductItem {
            addOverlay (){

               var task;
               clearInterval(task);
               task = setTimeout(function () {
                   $(".overlay").parent().addClass('pointer-none');
               }, 100);
            }
        };

    Registries.Component.extend(KsProductItem,ks_product_item);
    return KsProductItem;
})