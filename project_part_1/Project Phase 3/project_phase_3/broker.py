import os

from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import json
import requests
from database import database_tools

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app, cors_allowed_origins=['http://localhost:8101',
                                               'http://localhost:8201',
                                               'http://localhost:8202',
                                               'http://localhost:8203',
                                               'http://localhost:8001',
                                               'http://localhost:8002',
                                               'http://localhost:8003'])


# Connection Data
subscribers = {}     # key-value: subscriber socket and subscriber id
publishers = {}     # key-value: publisher socket and publisher id
brokers = [8001, 8002, 8003]      # tracks brokers


# Socket connections
@socketio.on('connect')
def test_connect(auth):
    print('Client connected: ' + request.sid)


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected: ' + request.sid)


@socketio.on('sub_login')
def sub_login(content):
    id_value = content['id']

    # Check that id exists in database
    result = database_tools.get_subscriber_topics(id_value)
    if result != -1:

        # join rooms
        print("Client joined subscribers")
        subscribers[request.sid] = id_value
        join_room(request.sid)
        join_room("subscriber")
        print("Current subscribers: ")
        print(subscribers)

        # get advertised topics
        advertised_topics = database_tools.get_all_filtered_events()

        # get subscribed topics
        subscribed_topics = database_tools.get_subscriber_topics(subscribers[request.sid])

        # get filtered events under subscribed topics
        events = {}
        for subscribed_topic in subscribed_topics:
            filtered_events = database_tools.get_filtered_events(subscribed_topic)
            for event in filtered_events:
                game_title = event['title']
                game_price = event['price']
                if game_title not in events:
                    events[game_title] = game_price

        # send data
        emit('login_response', {'data': id_value})
        emit('load', {'data': advertised_topics})
        emit('subscribed', {'data': subscribed_topics})
        for event in events:
            emit('notified', {'title': event, 'price': events[event]})
    else:
        emit('login_response', {'data': "error"})


@socketio.on('sub_create')
def sub_create(content):
    id_value = content['id']

    # Check that id does not exist in database
    result = database_tools.get_subscriber_topics(id_value)

    # If result is negative, emit success and add id to DB
    if result == -1:
        database_tools.add_subscriber(id_value)
        emit('create_response', {'data': id_value})
    else:
        emit('create_response', {'data': "error"})


@socketio.on('pub_login')
def pub_login(content):
    id_value = content['id']

    # Check that id exists in database
    result = database_tools.get_publisher(id_value)
    if result != -1:

        # join rooms
        print("Client joined publishers")
        publishers[request.sid] = id_value
        join_room(request.sid)
        join_room("publisher")
        print("Current publishers: ")
        print(publishers)

        # send data
        emit('login_response', {'data': id_value})
        data = database_tools.get_publisher(id_value)
        emit('load', {'topics': data['advertised'], 'counter': data['counter']})
    else:
        emit('login_response', {'data': "error"})


@socketio.on('pub_create')
def pub_create(content):
    id_value = content['id']

    # Check that id does not exist in database
    result = database_tools.get_publisher(id_value)

    # If result is negative, emit success and add id to DB
    if result == -1:
        database_tools.add_publisher(id_value)
        emit('create_response', {'data': id_value})
    else:
        emit('create_response', {'data': "error"})


@socketio.on('advertise')
def advertise(content):
    if request.sid in publishers:
        value = content['value']
        print("advertising..." + str(value))

        # get currently advertised topics
        publisher_list = list(publishers.values())
        advertised_topics = database_tools.get_publisher(publisher_list[0])['advertised']

        # add topic if not in advertised topics
        if value not in advertised_topics:
            database_tools.add_filter(value)
            result = database_tools.update_publisher(publisher_list[0], [value], -1)

            # emit if topic successfully added
            if result != -1:
                emit('advertised', {'data': result['advertised']}, room="publisher")
                emit('advertised', {'data': result['advertised']}, room="subscriber")


@socketio.on('deadvertise')
def deadvertise(content):
    if request.sid in publishers:
        value = content['value']
        print("deadvertising..." + str(value))

        # get currently advertised topics
        publisher_list = list(publishers.values())
        advertised_topics = database_tools.get_publisher(publisher_list[0])['advertised']

        # remove topic if in advertised topics
        if value in advertised_topics:
            database_tools.remove_filter(value)
            result = database_tools.update_publisher_remove(publisher_list[0], value)

            # emit if topic successfully added
            if result != -1:
                emit('advertised', {'data': result['advertised']}, room="publisher")
                emit('advertised', {'data': result['advertised']}, room="subscriber")


@socketio.on('subscribe')
def subscribe(content):
    if request.sid in subscribers:
        topic = content['value']
        print("subscribing..." + str(topic))

        # check if subscribed topic is in advertised topics and not already subscribed
        advertised_topics = database_tools.get_all_filtered_events()
        subscribed_topics = database_tools.get_subscriber_topics(subscribers[request.sid])
        if topic in advertised_topics and topic not in subscribed_topics:
            database_tools.update_subscriber(subscribers[request.sid], [topic])
            result = database_tools.get_subscriber_topics(subscribers[request.sid])
            emit('subscribed', {'data': result})


@socketio.on('unsubscribe')
def unsubscribe(content):
    if request.sid in subscribers:
        value = content['value']
        print("unsubscribing..." + str(value))
        database_tools.update_subscriber_remove(subscribers[request.sid], value)
        result = database_tools.get_subscriber_topics(subscribers[request.sid])
        emit('subscribed', {'data': result})


@socketio.on('publish')
def publish(content):
    if request.sid in publishers:
        print("publishing...")

        # extract data from content
        topics = content['topics']      # topics published event falls under
        counter = content['counter']    # number to events published by publisher
        game = content['game']          # {'title': game_title, 'price': game_price}

        # add data to database
        publisher_list = list(publishers.values())
        database_tools.update_publisher(publisher_list[0], [], counter)
        database_tools.add_event(game)
        for topic in topics:
            database_tools.update_filter(topic, game)

        # notify subscribers of topics related to new event
        for socket in subscribers:
            sub_filters = database_tools.get_subscriber_topics(subscribers[socket])

            # loop through subscriber's filters and check if event is related
            emitted = False  # prevent emitting same event more than once for each subscriber
            if sub_filters != -1:
                for topic in topics:
                    if topic in sub_filters and not emitted:
                        emit('notified', {'title': game['title'], 'price': game['price']}, room=socket)
                        emitted = True

        # notify other brokers through post requests
        for broker in brokers:
            if str(broker) != port:  # prevent sending to itself
                hostname = "project_phase_3_broker" + str(brokers.index(broker) + 1) + "_1"
                host = 'http://' + hostname + ':' + str(broker) + '/notify'
                print(host, flush=True)
                data = {'topics': topics, 'game': {'title': game['title'], 'price': game['price']}}
                headers = {"Content-Type": "application/json; charset=utf-8", 'Access-Control-Allow-Origin': '*'}
                json_data = json.dumps(data)
                res = requests.post(host, headers=headers, json=json_data)


@app.route('/', methods=['GET'])
def homepage():
    return render_template('subscriber.html')


@app.route('/notify', methods=['POST'])
def notify():
    print("receieved /notify", flush=True)
    # extract data from content
    content = json.loads(request.json)

    topics = content['topics']      # topics published event falls under
    game = content['game']          # {'title': game_title, 'price': game_price}

    print(subscribers, flush=True)
    # notify subscribers of topics related to new event
    for socket in subscribers:
        print(socket, flush=True)
        sub_filters = database_tools.get_subscriber_topics(subscribers[socket])

        # loop through subscriber's filters and check if event is related
        emitted = False  # prevent emitting same event more than once for each subscriber
        if sub_filters != -1:
            for topic in topics:
                if topic in sub_filters and not emitted:
                    result = {'title': game['title'], 'price': game['price']}
                    emit('notified', result, room=socket, namespace='/')
                    emitted = True
    return jsonify(success=True)


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=8000)
    port = os.environ.get('PORT')
    socketio.run(app, host='0.0.0.0', port=port)
