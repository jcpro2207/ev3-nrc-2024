# fix incorrect MIME types in Windows registry
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from flask import Flask, redirect, render_template, url_for

flask_app = Flask(__name__, static_folder="static", template_folder="templates")

# region routes
@flask_app.route("/")
def index():
    return render_template("index.html")

@flask_app.route("/interface")
def interface():
    return render_template("interface.html")

@flask_app.route("/camera")
def camera():
    return render_template("camera.html")

# redirects
@flask_app.route('/interface/')
def r_i():
    return redirect(url_for("interface"))
@flask_app.route('/camera/')
def r_c():
    return redirect(url_for("camera"))
# endregion