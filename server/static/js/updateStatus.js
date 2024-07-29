/* eslint-env browser */

const connStatusIndicator = document.getElementById("connection-status-indicator");
const vidStatusIndicator = document.getElementById("video-status-indicator");

// see CSS stylesheet for class names & colours for status codes
export default function updateStatus(connStatusText, connStatusCode, vidStatusText, vidStatusCode) {
	if (connStatusText) {
		connStatusIndicator.innerText = connStatusText;
		for (const $class of connStatusIndicator.classList) {
			connStatusIndicator.classList.remove($class);
		}
		connStatusIndicator.classList.add(`status-code-${connStatusCode}`);
	}

	if (vidStatusText) {
		vidStatusIndicator.innerText = vidStatusText;
		for (const $class of vidStatusIndicator.classList) {
			vidStatusIndicator.classList.remove($class);
		}
		vidStatusIndicator.classList.add(`status-code-${vidStatusCode}`);
	}
}
