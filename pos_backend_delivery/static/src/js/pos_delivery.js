'use strict';
odoo.define('pos_backend_delivery.delivery', function (require) {
    var tools = require('pos_backend_communication.tools');
    var session = require('web.session');
    var OrderSelectorWidget = require('point_of_sale.chrome').OrderSelectorWidget;
    var translation = require('web.translation');
    var _t = translation._t;
    var action_url = null;
    var pos_instance = null;
    
    function open_backend() {
      action_url = action_url || session.rpc(
        '/web/action/load', { "action_id":"pos_backend_delivery.simple_delivery_action"})
        .then(function (e) { return e.id; });
      action_url.then(function(action) {
          var url = '/web?#min=1&limit=30&view_type=list&model=stock.picking&action='+ action;
          var msg = {'type': 'delivery.show_deliveries'};
          tools.open_page(url, msg, 'delivery');
      });
    }

    OrderSelectorWidget.include({
      init: function(parent, options) {
        this._super(parent, options);
        pos_instance = this.pos;
        this.delivery_el = $('<span class="order-button delivery-button">'+
          '<span class="order-sequence">' + _t('Delivery') + '</span>' +
        '</span>').click(function () {
          open_backend()
        });
      },
      renderElement: function() {
          var self = this;
          this._super();
          this.delivery_el.appendTo(this.$el);
      }
    });
    return {
      callbacks: tools.callbacks
    };
});
