/* eslint-env browser */
/* global io */
/* eslint-disable no-console */

// import updateStatus from "./updateStatus.js";

const btnStream = document.getElementById("btn-stream");
const videoDisplay = document.getElementById("video-display");
const canvasEl = document.getElementById("canvas-el");
const ctx = canvasEl.getContext("2d");

const socket = io();

btnStream.addEventListener("click", async () => {
	const videoStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
	videoDisplay.srcObject = videoStream;

	const { width, height } = videoStream.getVideoTracks()[0].getSettings();
	canvasEl.width = width;
	canvasEl.height = height;

	function f() {
		ctx.drawImage(videoDisplay, 0, 0);
		const dataURL = canvasEl.toDataURL("image/jpg");

		// remove data:image/png;base64,
		const imageData = dataURL.slice(22);

		socket.emit("client-camera-frame", imageData);

		// window.requestAnimationFrame(f);

		setTimeout(f, 50);
	}
	// window.requestAnimationFrame(f);
	f();

	// socket.emit("client-camera-frame");
});

/*
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
*/
