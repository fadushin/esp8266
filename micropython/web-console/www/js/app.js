// 
// Copyright (c) dushin.net  All Rights Reserved
// 
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//     * Neither the name of dushin.net nor the
//       names of its contributors may be used to endorse or promote products
//       derived from this software without specific prior written permission.
// 
// THIS SOFTWARE IS PROVIDED BY dushin.net ``AS IS'' AND ANY
// EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL dushin.net BE LIABLE FOR ANY
// DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
// ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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

// var ap_config_view = new APConfigView({model: ap_config})
var ap_config_view = null;
setTimeout(function(){ap_config_view = new APConfigView({model: ap_config});}, 500);

