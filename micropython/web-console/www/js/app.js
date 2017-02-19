//
//     # ----------------------------------------------------------------------------
//     # "THE BEER-WARE LICENSE" (Revision 42):
//     # <fred@dushin.net> wrote this file.  You are hereby granted permission to
//     # copy, modify, or mutilate this file without restriction.  If you create a
//     # work derived from this file, you may optionally include a copy of this notice,
//     # for which I would be most grateful, but you are not required to do so.
//     # If we meet some day, and you think this stuff is worth it, you can buy me a
//     # beer in return.   Fred Dushin
//     # ----------------------------------------------------------------------------
//

var SystemModel = Backbone.Model.extend({
	url: '/api/system',
	defaults: {
		platform: null,
		version: null,
		system: null,
		machine_id: null,
		machine_freq: null
	},
	
	parse: function(data) {
		data.machine_freq = this.convert_frequency(data.machine_freq);
		data.platform = data.platform + "-" + data.version
		return data;
	},
	
	convert_frequency: function(freq) {
		if (freq > 1000000) {
			return (freq / 1000000) + "mhz";
		} else {
			return freq + "hz";
		}
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

var precision2 = function(number){
	return number.toPrecision(2);
};

var to_size_string = function(value) {
	var one_kb = 1024
	var one_mb = one_kb*1024
	if (value > one_mb) {
		return precision2(value/one_mb) + "mb";
	}
	else if (value > one_kb) {
		return precision2(value/one_kb) + "kb";
	} else {
		return value + "b";
	}
};

var MemoryModel = Backbone.Model.extend({
	url: '/api/memory',
	defaults: {
		mem_alloc: 10035,
		mem_free: 1234,
		// derived from above
		capacity: null,
		usage: 20,
	},
	
	parse: function(data) {
		var capacity = data.mem_alloc + data.mem_free;
		data.usage = Math.round((capacity - data.mem_free) / capacity * 100.0);
		data.capacity = to_size_string(capacity)
		data.mem_alloc = to_size_string(data.mem_alloc)
		data.mem_free = to_size_string(data.mem_free)
		return data;
	}
});
var memory_model = new MemoryModel();

var MemoryView = Backbone.View.extend({
	el: '#memory-view',
	template: _.template($('#memory-tmpl').html()),

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
var memory_view = new MemoryView({model: memory_model})

var FlashModel = Backbone.Model.extend({
	url: '/api/flash',
	defaults: {
		flash_id: null,
		flash_size: null,
		capacity: null,
		used: null,
		free: null,
		usage: null
	},
	
	parse: function(data) {
		data.usage = Math.round((data.capacity - data.free) / data.capacity * 100.0);
		data.flash_size = to_size_string(data.flash_size)
		data.capacity = to_size_string(data.capacity)
		data.used = to_size_string(data.used)
		data.free = to_size_string(data.free)
		return data;
	}
});
var flash_model = new FlashModel();

var FlashView = Backbone.View.extend({
	el: '#flash-view',
	template: _.template($('#flash-tmpl').html()),

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
var flash_view = new FlashView({model: flash_model})


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

var ap_config_model = new APConfigModel();

// var ap_config_view = new APConfigView({model: ap_config})
var ap_config_view = null;
setTimeout(function(){ap_config_view = new APConfigView({model: ap_config_model});}, 500);




var ModalAPConfigView = Backbone.View.extend({
	el: '#ap-config-modal-content',
	template: _.template($('#ap-config-modal-tmpl').html()),
	
	events: {
		'change .hidden': 'onChangeHidden',
		'change .authmode': 'onChangeAuthMode',
		'change .essid': 'onChangeEssid',
		'click .save': 'onSave'
	},
	
	initialize: function() {
		this.listenTo(this.model, 'sync change', this.render);
		this.model = ap_config_model.clone();
		this.render();
	},

	onChangeHidden: function(evt) {
		this.model.set('hidden', evt.currentTarget.value);
	},

	onChangeAuthMode: function(evt) {
		this.model.set('authmode', evt.currentTarget.value);
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
var ap_config_modal_view = new ModalAPConfigView({model: new APConfigModel()});

