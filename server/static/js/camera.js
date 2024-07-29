/* eslint-env browser */
/* global Daily */
/* eslint-disable no-console */

import updateStatus from "./updateStatus.js";

const btnStream = document.getElementById("btn-stream");
const videoDisplay = document.getElementById("video-display");

let connected = false;
updateStatus("not connected", 0, "not connected", 0);

const DAILY_ROOM_URL = "https://purplish.daily.co/purplish";

const call = Daily.createCallObject({
	url: DAILY_ROOM_URL,
	videoSource: true,
	audioSource: false,
});

call.on("loading", () => {
	updateStatus("connecting...", 1, "requesting permission", 1);
});

call.on("joined-meeting", (ev) => {
	const localParticipant = ev.participants.local;
	console.log("local participant object:", localParticipant);

	videoDisplay.srcObject = new MediaStream([localParticipant.videoTrack]);

	connected = true;
	updateStatus("connected", 2, "streaming", 2);

	btnStream.disabled = false;
	btnStream.innerText = "Stop streaming";
});

call.on("left-meeting", () => {
	updateStatus("disconnected", 0, "disconnected", 0);

	btnStream.disabled = false;
	btnStream.innerText = "Re-stream";
	connected = false;
});

call.on("error", console.log);

btnStream.addEventListener("click", () => {
	if (connected === false) {
		btnStream.disabled = true;
		call.join();
	} else {
		btnStream.disabled = true;
		call.leave();
	}
});
