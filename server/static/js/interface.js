/* eslint-env browser */
/* global io */
/* eslint-disable no-console */

const SOCKETIO_EVENT_NAME = "data-url";

const socket = io();

const imgEl = document.getElementById("img-el");

socket.on(SOCKETIO_EVENT_NAME, (data) => {
	imgEl.src = data;
});
