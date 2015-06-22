var ws;

function init() {
	ws = new WebSocket("ws://" + window.location.hostname + ":" + window.location.port + "/ws");

	// ws.send(JSON.stringify({'cmd': 'connect', 'gid': gid}))

	ws.onmessage = function(e) {
		alert(e.data);
	};
}

function send(message) {
	ws.send(message)
}

window.onload = function() {
	init();
};
