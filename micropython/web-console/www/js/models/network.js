// network.js

var Network = Backbone.Model.extend({
  url: '/api/network',
  defaults: {
    id: null,
    //name: null,
    //occupation: null
  }
});

var network = new Network();