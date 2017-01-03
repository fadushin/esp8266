// app.js

var SystemModel = Backbone.Model.extend({
	url: '/api/system',
	defaults: {
		// id: null,
		platform: null,
		version: null,
		system: null,
		machine_id: null,
		machine_freq: null
	}
});
var system_model = new SystemModel();

var SystemView = Backbone.View.extend({
	el: '#system-view',
	template: _.template($('#system-tmpl').html()),

	initialize: function() {
		this.listenTo(this.model, 'sync change', this.render);
		this.model.fetch();
		this.render();
	},
	
	render: function() {
		var html = this.template(this.model.toJSON());
		this.$el.html(html);
		return this;
	}
});
var system_view = new SystemView({model: system_model})


var APConfigModel = Backbone.Model.extend({
	url: '/api/network/ap/config',
	defaults: {
		// id: null,
		authmode: null,
		hidden: null,
		mac: null,
		channel: null,
		essid: null
	}
});

var APConfigView = Backbone.View.extend({
	el: '#ap-config-view',
	template: _.template($('#ap-config-tmpl').html()),
	
	events: {
		'change .essid': 'onChangeEssid',
		'click .save': 'onSave'
	},
	
	initialize: function() {
		this.listenTo(this.model, 'sync change', this.render);
		this.model.fetch();
		this.render();
	},

	onChangeEssid: function(evt) {
		this.model.set('essid', evt.currentTarget.value);
	},

	onSave: function(evt) {
		this.model.save();
	},

	render: function() {
		var html = this.template(this.model.toJSON());
		this.$el.html(html);
		return this;
	}
});

var ap_config = new APConfigModel();
var ap_config_view = new APConfigView({model: ap_config})
