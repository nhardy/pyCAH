var ws;
var gid = parseInt((/\/game\/(\d+)/i).exec(window.location.pathname)[1]);

function init() {
	ws = new WebSocket("ws://" + window.location.hostname + ":" + window.location.port + "/ws");

	ws.onopen = function() {
		ws.send(JSON.stringify({"cmd": "connect", "gid": gid}));
	};

	ws.onmessage = function(e) {
		var content = JSON.parse(e.data);
		var cmd = content["cmd"];
		switch(cmd){
			case "players":
				document.getElementById("players").innerHTML = content["players"];
				break;
			case "chat":
				document.getElementById("chat").innerHTML += "<p>&lt;" + content["sender"] + "&gt;: " + content["message"] + "</p>\n";
				break;
		}
	};
}

function chat() {
	var messageBox = document.getElementById("message");
	var message = messageBox.value;
	ws.send(JSON.stringify({"cmd": "chat", "message": message}));
	messageBox.value = "";
}

window.onload = function() {
	init();
};
window.onbeforeunload = function() {
	ws.onclose = function () {};
	ws.close();
};
