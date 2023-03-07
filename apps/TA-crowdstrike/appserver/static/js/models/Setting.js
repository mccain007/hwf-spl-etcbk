/*global define*/
define([
    'underscore',
    'app/models/Base.Model',
    'app/config/ContextMap'
], function (
    _,
    BaseModel,
    ContextMap
) {
    return BaseModel.extend({
        url: [
            ContextMap.restRoot,
            ContextMap.setting
        ].join('/'),

        initialize: function (attributes, options) {
            options = options || {};
            this.collection = options.collection;
            BaseModel.prototype.initialize.call(this, attributes, options);
            this.addValidation('proxy_enabled', this.validHostAndPort);
        },

        validHostAndPort: function (attr) {
            if (this.entry.attributes.name === "crowdstrike_proxy") {
                var val = this.entry.content.get(attr),
                    proxy_url = this.entry.content.get("proxy_url"),
                    proxy_port = this.entry.content.get("proxy_port"),
                    proxy_port_empty = false,
                    proxy_url_empty = false;
                if (proxy_url && String(proxy_url).replace(/^\s+|\s+$/gm, '')) {
                    var re = /^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$/;
                    if (!String(proxy_url).replace(/^\s+|\s+$/gm, '').match(re)) {
                        return _('Field "Host" is not in the allowed format').t();
                    }
                }
                if (Number(val) === 1) {
                    if (!proxy_url || !String(proxy_url).replace(/^\s+|\s+$/gm, '')) {
                        return _('Field "Host" is required').t();
                    }
                    if (isNaN(Number(proxy_port)) || Number(proxy_port) < 1 || Number(proxy_port) > 65535) {
                        return _('Field "Port" should be in range (1, 65535)').t();
                    }
                } else {
                    proxy_port_empty = proxy_url || String(proxy_url).replace(/^\s+|\s+$/gm, '');
                    proxy_url_empty = proxy_port || String(proxy_port).replace(/^\s+|\s+$/gm, '');
                    //Proxy_url and Proxy_port can not be empty at the same time
                    if (proxy_port_empty && !proxy_url_empty) {
                        return _('Field "Port" is required').t();
                    }
                    if (!proxy_port_empty && proxy_url_empty) {
                        return _('Field "Host" is required').t();
                    }
                    //Check the proxy_port in the right range
                    if (proxy_port || String(proxy_port).replace(/^\s+|\s+$/gm, '')) {
                        if (isNaN(Number(proxy_port)) || Number(proxy_port) < 1 || Number(proxy_port) > 65535) {
                            return _('Field "Port" should be in range (1, 65535)').t();
                        }
                    }
                }
            }
        }
    });
});
