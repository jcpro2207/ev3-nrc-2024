/* eslint-env browser */
/* global io */
/* eslint-disable no-console */

const SOCKETIO_EVENT_NAME = "data-url";
const B64_PREFIX = "data:image/jpeg;base64,";

const socket = io();

const imgEl = document.getElementById("img-el");
const fpsDisplay = document.getElementById("fps-display");

let last = performance.now();

socket.on(SOCKETIO_EVENT_NAME, (b64ImageData) => {
	imgEl.src = `${B64_PREFIX}${b64ImageData}`;

	const now = performance.now();
	// 1 (sec) / time diff (sec)
	const fpsUnrounded = 1 / ((now - last) / 1000);
	fpsDisplay.innerText = Math.round(fpsUnrounded * 100) / 100;
	last = now;
});
