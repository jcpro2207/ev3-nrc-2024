# fix incorrect MIME types in Windows registry
import mimetypes

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from flask import Flask, redirect, render_template, url_for
from flask_socketio import SocketIO

import socket
from colour_detection_loop import colour_detection_loop

from concurrent.futures import ThreadPoolExecutor

PORT = 8000
CLIENT_WEBCAM = False

# address of the bluetooth device of this computer (the one you are using right now)
# JC's address: E4:B3:18:64:F3:DD
BLUETOOTH_ADDRESS = "E4:B3:18:64:F3:DD" 
CHANNEL = 5 # random number

flask_app = Flask(__name__, static_folder="static", template_folder="templates")
socketio_app = SocketIO(flask_app)

# region ROUTES
# redirects
@flask_app.route('/interface/')
def r_i():
    return redirect(url_for("interface"))

@flask_app.route('/camera/')
def r_c():
    return redirect(url_for("camera"))


@flask_app.route("/")
def index():
    return render_template("index.html")

@flask_app.route("/interface")
def interface():
    return render_template("interface.html")

@flask_app.route("/camera")
def camera():
    return render_template("camera.html")
# endregion

# region colour detection
if not CLIENT_WEBCAM:
    print("camera: webcam on server device")

    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as server_sock:
        print(f"\n[Bluetooth] Created server socket {server_sock}.")

        server_sock.bind((BLUETOOTH_ADDRESS, CHANNEL))
        server_sock.listen(1)

        print("\n[Bluetooth] Waiting for socket connection from client (EV3)...")

        client_sock, address = server_sock.accept()

        print(f"\n[Bluetooth] Accepted connection from client socket:")
        print(f"{client_sock}, address {address}")
        print("\nCurrent `server_sock`:", server_sock)

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(colour_detection_loop, socketio_app, client_sock)

        if __name__ == "__main__":
            socketio_app.run(
                app = flask_app,
                host = "0.0.0.0",
                port = PORT,
                debug = True,
                use_reloader = False,
                log_output = True,
                # generate self-signed SSL certificate (so that getUserMedia isn't auto-disabled in browsers)
                ssl_context = "adhoc"
            )
# endregion
