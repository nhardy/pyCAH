var ws;
var gid = parseInt((/\/game\/(\d+)/i).exec(window.location.pathname)[1]);

function init() {
	ws = new WebSocket("ws://" + window.location.hostname + ":" + window.location.port + "/ws");

	ws.onopen = function() {
		ws.send(JSON.stringify({"cmd": "connect", "gid": gid}));
	};

	ws.onclose = function() {
		var chat = document.getElementById("chat");
		chat.innerHTML += "<p>&lt;[SYSTEM]&gt;: Lost connection... Retrying...</p>\n";
		chat.scrollTop = chat.scrollHeight;
		init();
	};

	ws.onmessage = function(e) {
		var content = JSON.parse(e.data);
		var cmd = content["cmd"];
		switch(cmd){
			case "players":
				var players_html = "";
				for (var p = 0; p < content["players"].length; p++) {
					players_html += "<p>" + content["players"][p] + "</p>\n";
				}
				document.getElementById("players").innerHTML = players_html
				break;
			case "chat":
				var chat = document.getElementById("chat");
				chat.innerHTML += "<p>&lt;" + content["sender"] + "&gt;: " + content["message"] + "</p>\n";
				chat.scrollTop = chat.scrollHeight;
				break;
			case "new_round":
				var game_html = "";
				var gameDiv = document.getElementById("game");
				var czar = content["czar"];
				var card_value = content["value"];
				var hand = content["hand"];
				game_html += "<p>Czar: " + czar + "</p>\n<p>Black Card: " + card_value + "</p>\n";
				game_html += "<ul>\n";
				for (var c = 0; c < hand.length; c++) {
					game_html += "<li><a href=\"javascript:playCard(" + hand[c]["eid"] + ", " + hand[c]["cid"] + ");\">" + hand[c]["value"] + "</a></li>\n";
				}
				game_html += "</ul>\n";
				gameDiv.innerHTML = game_html;
				break;
			case "vote_required":
				alert(content["hands"]);
				var hand = parseInt(prompt("Enter hand number (0 indexed): "));
				ws.send(JSON.stringify({"cmd": "vote", "hand": content["hands"][hand]}))
				break;
			default:
				alert(e.data);
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

function join() {
	ws.send(JSON.stringify({"cmd": "join"}));
	document.getElementById("game").innerHTML = "<p>Waiting...</p>\n";
}

function playCard(eid, cid) {
	ws.send(JSON.stringify({"cmd": "white_card", "eid": eid, "cid": cid}));
}

window.onload = function() {
	init();
};
window.onbeforeunload = function() {
	ws.onclose = function () {};
	ws.close();
};
