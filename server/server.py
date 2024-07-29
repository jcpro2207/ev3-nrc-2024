# fix incorrect MIME types in Windows registry
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from numpy.typing import NDArray
from flask import Flask, redirect, render_template, url_for, Response
from flask_socketio import SocketIO
import cv2
import base64

from concurrent.futures import ThreadPoolExecutor

PORT = 8000
SOCKETIO_EVENT_NAME = "data-url"

flask_app = Flask(__name__, static_folder="static", template_folder="templates")
socketio_app = SocketIO(flask_app)

current_data_url = ""

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

# region AI
executor = ThreadPoolExecutor(max_workers=1)

def ndarray_to_dataurl(ndarray: NDArray):
    return "data:image/jpeg;base64," + base64.b64encode(ndarray.tobytes()).decode()

def AI_loop():
    from AI import run_AI_and_get_frame

    global current_data_url

    while True:
        frame = run_AI_and_get_frame()
        (retval, jpg_image) = cv2.imencode(".jpg", frame)

        # skip this frame if image encoding was unsuccessful
        if retval is False:
            continue

        current_data_url = ndarray_to_dataurl(jpg_image)

        socketio_app.emit(SOCKETIO_EVENT_NAME, current_data_url)

executor.submit(AI_loop)
# endregion

if __name__ == "__main__":
    socketio_app.run(app=flask_app, port=PORT, use_reloader=False, log_output=True)
