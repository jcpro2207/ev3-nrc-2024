/* eslint-env browser */
/* global Daily */
/* eslint-disable no-console */

const btnJoin = document.getElementById("btn-join");

const DAILY_ROOM_URL = "https://purplish.daily.co/purplish";

const call = Daily.createCallObject({
	url: DAILY_ROOM_URL,
	videoSource: false,
	audioSource: false,
});

call.on("loading", () => {
	console.log("loading meeting");

	btnJoin.disabled = true;
	btnJoin.innerText = "Loading...";
});

// "[`joined-meeting` event]: The participants list will only ever include the local participant. This is because the server sends participant information in batches of 50 after this initial joined event occurs [...] To get detailed participant information, listen for the `participant-joined` event, sent in conjunction with the batched updates." - daily docs
call.on("joined-meeting", (ev) => {
	console.log("joined meeting");
	console.log("local participant object:", ev.participants.local);

	btnJoin.innerText = "Connected";
});

call.on("participant-joined", (ev) => {
	const { participant } = ev;

	console.log("participant joined:", participant);
});

call.on("track-started", (ev) => {
	const videoElement = document.getElementById("video-element");
	videoElement.srcObject = new MediaStream([ev.track]);
});

call.on("error", console.log);

btnJoin.addEventListener("click", () => call.join());

