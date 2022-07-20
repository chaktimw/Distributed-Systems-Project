import os

from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import json
import requests

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)


# Routes
@app.route('/', methods=['GET'])
def homepage():
    port = os.environ.get('PORT')
    socket_port = int(port) - 200
    return render_template('subscriber.html', connect=str(socket_port))


@app.route("/static/<path:name>")
def static_content(name):
    return send_from_directory(
        'static', name
    )


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=8000)
    port = os.environ.get('PORT')
    socketio.run(app, host='0.0.0.0', port=port)
