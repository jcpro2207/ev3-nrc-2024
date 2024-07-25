import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import express from "express";
import Daily from "@daily-co/daily-js";
import chalk from "chalk";

// ~ CONSTANTS
const PORT = 8000;
const __dirname = dirname(fileURLToPath(import.meta.url));

// ~ LOGGING FUNCTIONS
const currentTime = () => {
	const now = new Date(Date.now());
	return `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
};

const {
	blueBright, cyan, green, magenta,
} = chalk;
const info = (text) => console.log(
	chalk.gray(`[${currentTime()}]`),
	chalk.yellowBright(text),
);
const log = (text) => console.log(
	chalk.gray.italic(`[${currentTime()}]`),
	chalk.blue.italic(text),
);

// ~ EXPRESS
const app = express();

// redirect these routes to /interface
for (const route of ["/", "/interface.html", "/index", "/index.html"]) {
	app.all(route, (req, res) => res.redirect("/interface"));
}
// serve public/interface/interface.html file at /interface route
app.get("/interface", (req, res) => {
	res.sendFile(`${__dirname}/public/interface/interface.html`);

	log(`${green(req.ip)} connected to ${cyan("/interface")} [User-Agent: ${magenta(req.get("User-Agent"))}]`);
});

// redirect these routes to /camera
for (const route of ["/camera.html", "/camera/camera.html", "/camera/camera"]) {
	app.all(route, (req, res) => res.redirect("/camera"));
}
// serve public/camera/camera.html file at /camera route
app.get("/camera", (req, res) => {
	res.sendFile(`${__dirname}/public/camera/camera.html`);

	log(`${green(req.ip)} connected to ${cyan("/camera")} [User-Agent: ${magenta(req.get("User-Agent"))}]`);
});

// serve all other files in /public as static files
app.use(express.static(join(__dirname, "public")));

const server = app.listen(PORT, () => {
	info(`Server listening at ${blueBright(`localhost:${PORT}`)}`);
});
