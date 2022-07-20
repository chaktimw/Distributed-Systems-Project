from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import json
import requests
from database import publisher_tools, test_database_tools, database_tools

app = Flask(__name__, template_folder='templates')
app.config['MONGODB_SETTINGS'] = {
    'db': 'test_database',
    'host': 'mongo',
    'port': 27017
}
socketio = SocketIO(app)


# get API data
def get_data():
    r = requests.get("https://www.cheapshark.com/api/1.0/deals?")
    content = json.loads(r.content)
    return content


subscribers = []  # Tracks connected subscribers
publishers = []   # Tracks connected publishers
data = {
    "counter": database_tools.get_tracker(),    # Tracks number of titles published
    "raw_data": get_data()                      # List of dictionaries (each dict is a game) from API
}


# Routes
@app.route('/', methods=['GET'])
def homepage():
    print(data["counter"])
    return render_template('index.html')


@app.route('/subscriber', methods=['GET'])
def subpage():
    return render_template('subscriber.html')


@app.route('/publisher', methods=['GET'])
def pubpage():
    return render_template('publisher.html')


@app.route("/static/<path:name>")
def staticFolder(name):
    return send_from_directory(
        'static', name
    )


# Socket connections
@socketio.on('connect')
def test_connect(auth):
    print('Client connected: ' + request.sid)


@socketio.on('disconnect')
def test_disconnect():
    user = request.sid
    if user in subscribers:
        database_tools.remove_subscriber(user)
        subscribers.remove(user)
    if user in publishers:
        publishers.remove(user)
    print('Client disconnected: ' + request.sid)


@socketio.on('join')
def on_join(content):
    room = content['room']
    if room == "publisher":
        print("Client joined publishers")
        publishers.append(request.sid)
        print("Current publishers: ")
        print(publishers)
        emit('load', {'data': publisher_tools.get_advertised()})
    else:
        print("Client joined subscribers")
        subscribers.append(request.sid)
        join_room(request.sid)
        database_tools.add_subscriber(request.sid)
        print("Current subscribers: ")
        print(subscribers)
        emit('load', {'data': publisher_tools.get_advertised()})
    join_room(room)
    # emit('load', {'data': 'Connected: ' + request.sid}, room=room)


@socketio.on('advertise')
def advertise(content):
    value = content['value']
    print("advertising..." + str(value))
    result = publisher_tools.advertise(value)
    emit('advertised', {'data': result}, room="publisher")
    emit('advertised', {'data': result}, room="subscriber")


@socketio.on('deadvertise')
def deadvertise(content):
    value = content['value']
    print("deadvertising..." + str(value))
    result = publisher_tools.deadvertise(value)
    emit('advertised', {'data': result}, room="publisher")
    emit('advertised', {'data': result}, room="subscriber")


@socketio.on('subscribe')
def subscribe(content):
    value = content['value']
    print("subscribing..." + str(value))
    current = publisher_tools.get_advertised()
    if value in current:
        database_tools.update_subscriber(request.sid, [value])
        result = database_tools.get_subscriber_topics(request.sid)
        emit('subscribed', {'data': result})


@socketio.on('unsubscribe')
def unsubscribe(content):
    value = content['value']
    print("unsubscribing..." + str(value))
    database_tools.update_subscriber_remove(request.sid, value)
    result = database_tools.get_subscriber_topics(request.sid)
    emit('subscribed', {'data': result})


@socketio.on('publish')
def publish(content):
    print("publishing...")
    result_tuple = publisher_tools.publish(data)
    data['counter'] += 1
    database_tools.update_tracker()
    game_title = result_tuple[0]
    game_price = result_tuple[1]
    filter_results = result_tuple[2]
    for id in subscribers:
        sub_filters = database_tools.get_subscriber_topics(id)
        emitted = False
        if sub_filters != -1:
            for filter_val in filter_results:
                print(sub_filters)
                print(filter_val)
                if filter_val in sub_filters and not emitted:
                    emit('notified', {'data': game_title, 'price': game_price}, room=id)
                    emitted = True
    emit('published', {'data': game_title, 'price': game_price})


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=8000)
    socketio.run(app, host='0.0.0.0', port=8000)
