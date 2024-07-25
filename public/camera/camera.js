/* eslint-env browser */
/* global Daily */
/* eslint-disable no-console */

const btnJoin = document.getElementById("btn-join");

const DAILY_ROOM_URL = "https://purplish.daily.co/purplish";

const call = Daily.createCallObject({
	url: DAILY_ROOM_URL,
	videoSource: true,
	audioSource: false,
	// dailyConfig: {
	// 	userMediaVideoConstraints: {
	// 		video: {
	// 			width: { ideal: 9999 },
	// 			height: { ideal: 9999 },
	// 		},
	// 	},
	// },
});

const updateStatus = (statusText, statusCode) => {
	if (!btnJoin.disabled) btnJoin.disabled = true;
	btnJoin.innerText = statusText;

	for (const $class of btnJoin.classList) btnJoin.classList.remove($class);
	// see CSS stylesheet for class names & colours
	btnJoin.classList.add(`status-code-${statusCode}`);
};

call.on("loading", () => {
	updateStatus("Loading...", 0);
});

call.on("joined-meeting", (ev) => {
	const localParticipant = ev.participants.local;
	console.log("local participant object:", localParticipant);

	const videoElement = document.getElementById("video-element");
	videoElement.srcObject = new MediaStream([localParticipant.videoTrack]);

	updateStatus("Streaming", 1);
});

call.on("error", console.log);

btnJoin.addEventListener("click", () => call.join());
