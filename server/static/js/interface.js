/* eslint-env browser */
/* global Daily */
/* eslint-disable no-console */

import updateStatus from "./updateStatus.js";

const btnJoin = document.getElementById("btn-join");
const videoDisplay = document.getElementById("video-display");

let connected = false;
updateStatus("not connected", 0, "not connected", 0);

const DAILY_ROOM_URL = "https://purplish.daily.co/purplish";

const call = Daily.createCallObject({
	url: DAILY_ROOM_URL,
	videoSource: false,
	audioSource: false,
});

call.on("loading", () => {
	console.log("event `loading`");

	updateStatus("connecting...", 1, null, null);
});

// "[`joined-meeting` event]: The participants list will only ever include the local participant. This is because the server sends participant information in batches of 50 after this initial joined event occurs [...] To get detailed participant information, listen for the `participant-joined` event, sent in conjunction with the batched updates." - daily docs
call.on("joined-meeting", () => {
	console.log("event `joined-meeting`");
	// console.log("local participant object:", ev.participants.local);

	connected = true;
	updateStatus("connected", 2, "waiting for video...", 1);

	btnJoin.innerText = "Disconnect";
	btnJoin.disabled = false;
});

call.on("left-meeting", () => {
	console.log("event `left-meeting`");
	updateStatus("disconnected", 0, "disconnected", 0);

	btnJoin.disabled = false;
	btnJoin.innerText = "Reconnect";
	connected = false;
});

call.on("participant-joined", () => {
	console.log("event `participant-joined`");
});

call.on("track-started", async (ev) => {
	console.log("event `track-started`:", ev);

	const { track, participant } = ev;
	if (track.kind !== "video") return;

	console.log("the participant joined at", participant.joined_at.toLocaleTimeString());

	videoDisplay.srcObject = new MediaStream([track]);
	updateStatus(null, null, "streaming", 2);
});

call.on("track-stopped", (ev) => {
	console.log("event `track-stopped`:", ev);

	updateStatus(null, null, "not streaming", 0);
});

call.on("error", console.log);

btnJoin.addEventListener("click", () => {
	console.log("btnJoin clicked");

	if (connected === false) {
		btnJoin.disabled = true;
		call.join();
	} else {
		btnJoin.disabled = true;
		call.leave();
	}
});
