'use strict';
odoo.define('pos_backend_delivery.delivery_back', function (require) {
    /*
     * Remove the ability to choose a partner from the POS
     * Instead: when the user clicks on the "Order button"
     * the backoffice load in another page (or tab) of the browser
     * She then picks a client and a custom js (still in backoffice) sends
     * back to this widget the id of the partner
     * This widget retrieve the partner through webservice and trigger an "Alert"
     * to get the focus back.
     *
     * */
    var translation = require('web.translation');
    var _t = translation._t;

    var tools = require('pos_backend_communication.back');

    if (tools.is_tied_to_pos()) {
        tools.callbacks['delivery.show_deliveries'] = function() {
            //get focus with alert
            //TODO: replace with notifications
            alert(_t('Ready'));
        };
        //tell the POS we are ready to receive
        tools.sendMessage({type: 'delivery.ready'});
    }
});