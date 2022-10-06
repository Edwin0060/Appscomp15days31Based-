odoo.define('pos_order_total_rounding_app.screens', function (require) {
"use strict";

	const OrderWidget = require('point_of_sale.OrderWidget');
	const models = require('point_of_sale.models');
	const core = require('web.core');
	const Registries = require('point_of_sale.Registries');
	var utils = require('web.utils');
	var field_utils = require('web.field_utils')
	var QWeb = core.qweb;
	var _t = core._t;

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attr, options) {
			_super_order.initialize.call(this,attr,options);
			this.round_amount = this.round_amount || "";
			this.round_product = this.round_product || "";           
		},
		
		get_round_amount: function(round){
			var total = round;
			if(total)
			{
				var decimal=total.toString().split('.');
				if (!decimal[1])
				{
					decimal[1]="0.0"
				}
				var decimal_round=decimal[1].split('');
				if (!decimal_round[1])
				{
					decimal_round[1]="0"
				}                
				if (parseInt(decimal_round[1])==1 || parseInt(decimal_round[1])==2)
				{
					x=decimal_round[1].toString();
					x="0";
					decimal_round=parseInt((decimal_round[0]+''+x));
				}
				else if(parseInt(decimal_round[1])==3 || parseInt(decimal_round[1])==4 || parseInt(decimal_round[1])==5 || parseInt(decimal_round[1])==6 || parseInt(decimal_round[1])==7)
				{                   
					x=decimal_round[1].toString();
					x="5"
					decimal_round=parseInt((decimal_round[0]+''+x));                   
				}           
				else if(parseInt(decimal_round[1])==8 || parseInt(decimal_round[1])==9)
				{                    
					x=decimal_round[1].toString();
					x="0";
					if (parseInt(decimal_round[0])==9)
					{
						var k=parseInt(decimal[0]) + 1;                        
						decimal[1]="0";
						var l=parseFloat(k+'.'+decimal[1])                      
						var m=l-total                       
						return parseFloat(m.toFixed(2));
					}
					else
					{
						var y=parseInt(decimal_round[0]) + 1;                   
						decimal_round=parseInt((y+''+x));
					}                    
				}
				else
				{
					x=decimal_round[1].toString();
					x="0"
					decimal_round=parseInt((decimal_round[0]+''+x));               
				}
				var x=parseFloat(decimal[0]+'.'+decimal_round)
				var round_total = Math.round(total)
				var round = round_total - total
				var r=round
				//var r=x-total
				return parseFloat(r.toFixed(2));
			}
			else
			{
				return 0;
			}         
		},
		get_total_with_tax_without_round:function()
		{
			return this.get_total_without_tax() + this.get_total_tax();
		},
		get_total_with_tax: function()
		{            
			if(this.pos.config.is_enable_rounding)
			{                   
				var get_total=this.get_total_without_tax() + this.get_total_tax();               
				var get_round_total= get_total + this.get_round_amount(get_total);
				return parseFloat(get_round_total.toFixed(2));
			}
			else
			{
				return this.get_total_without_tax() + this.get_total_tax();
			}
		},       
		export_as_JSON: function()
		{
			var json = _super_order.export_as_JSON.call(this);
			var get_total=this.get_total_without_tax() + this.get_total_tax();
			json.round_amount = this.get_round_amount(get_total);
			json.round_product = this.pos.config.rounding_product_id[0];
			if(json.round_amount != 0) 
			{               
				json.lines.push([0, 0, {'qty': 1, 'price_unit': json.round_amount, 'price_subtotal': json.round_amount, 'price_subtotal_incl': json.round_amount, 'product_id': json.round_product}])  
			}   
			return json;


		},
		init_from_JSON: function(json)
		{
			_super_order.init_from_JSON.apply(this,arguments);
			this.round_amount = json.round_amount;
			this.round_product = json.round_product;
		},       
	});
	

	const PosRoundOrderWidget = (OrderWidget) =>
		class extends OrderWidget {
			_updateSummary(){
				const get_tax= this.order ? this.order.get_total_with_tax_without_round() : 0; 
				const total = this.order ? this.order.get_total_with_tax() : 0;
				const tax = this.order ? get_tax - this.order.get_total_without_tax() : 0;
				this.state.total = this.env.pos.format_currency(total);
				this.state.tax = this.env.pos.format_currency(tax);
				if(this.order.pos.config.is_enable_rounding)
				{
					var getround_total = this.order.get_total_without_tax() + this.order.get_total_tax();
					var round = this.order ? this.order.get_round_amount(getround_total) : 0;
					this.state.round = this.env.pos.format_currency(round);
				}
				this.render();
			}
		};
	Registries.Component.extend(OrderWidget, PosRoundOrderWidget);

	return OrderWidget;
});
