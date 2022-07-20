import os

from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import json
import requests

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)


# get API data
def get_data():
    r = requests.get("https://www.cheapshark.com/api/1.0/deals?")
    content = json.loads(r.content)
    return content


clients = []
data = {
    "topics": [],           # contains topics advertised by this publisher
    "counter": -1,          # tracks number of titles published
    "raw_data": get_data()  # list of dictionaries (each dict is a game) from API
}


# Routes
@app.route('/', methods=['GET'])
def homepage():
    return render_template('publisher.html')


@app.route("/static/<path:name>")
def static_content(name):
    return send_from_directory(
        'static', name
    )


# Socket connections
@socketio.on('connect')
def test_connect(auth):
    clients.append(request.sid)
    join_room(request.sid)
    print('Client connected: ' + request.sid)


@socketio.on('disconnect')
def test_disconnect():
    clients.remove(request.sid)
    print('Client disconnected: ' + request.sid)


@socketio.on('load_data')
def received(content):
    data['topics'] = content['topics']
    data['counter'] = content['counter']


@socketio.on('update')
def received(content):
    data['topics'] = content['data']


@socketio.on('publish')
def publish(content):
    print("publishing...")

    # get api data
    counter = data['counter']
    raw_data = data['raw_data']
    raw_game = raw_data[counter]
    price = raw_game['salePrice']
    title = raw_game['title']
    game = {
        'title': title,
        'price': price
    }
    # update counter
    data['counter'] += 1

    # get topics related to game
    topics = data['topics']
    related_topics = []
    for topic in topics:
        if int(float(price)) < topic:
            related_topics.append(topic)

    # emit data
    emit('published', {'topics': related_topics, 'counter': data['counter'], 'game': game})


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=8000)
    port = os.environ.get('PORT')
    socketio.run(app, host='0.0.0.0', port=port)
