odoo.define('web_search_debounce.debounce', function (require) {
    'use strict';
    var core = require('web.core');
    var form = core.form_widget_registry.get('many2one');

    form.include({
        DEBOUNCE_TIMEOUT: 800,
        get_search_result: function(search) {
            var my_super = this._super.bind(this);
            var self = this;
            if (!self.promise) {
                //no promise defined : intitialize one.
                self.promise = $.Deferred();
                self.promise.then(function(d) { //clean up when we are done
                    self.promise = null;
                    return d;
                });
            }
            //re-use the debounced func
            self.deb = self.deb || _.debounce(function(promise, search) {
                //after the timeout,
                // trigger the search with the last input 'search'
                // and propagate the result through 'promise'
                promise.resolve(my_super(search));
            }, self.DEBOUNCE_TIMEOUT);
            self.deb(self.promise, search);
            return self.promise.then(function(d) {
                //don't know why return self.promise.promise() don't work.
                return d;
            });
        }
    });
});
