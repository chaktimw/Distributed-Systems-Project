import os
from time import sleep
from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
from kafka import KafkaConsumer, TopicPartition
from json import loads

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)
topics = []
events = 0

# Create consumer object
sleep(10)  # ensure all containers are ready
consumer = KafkaConsumer(
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=None,
    value_deserializer=lambda m: loads(m.decode('utf-8')),
    bootstrap_servers=['kafka-1:9092', 'kafka-2:9092', 'kafka-3:9092'])

# Consumer topics list
subscribed = []


# Routes
@app.route('/', methods=['GET'])
def homepage():
    port = os.environ.get('PORT')
    socket_port = int(port)
    return render_template('subscriber.html', connect=str(socket_port))


@app.route("/static/<path:name>")
def static_content(name):
    return send_from_directory(
        'static', name
    )


# Socket Connection
@socketio.on('connect')
def test_connect(auth):
    emit('subscribed', {'data': subscribed})
    print('Client connected: ' + request.sid)


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected: ' + request.sid)


# Subscribe to new topic
@socketio.on('subscribe')
def subscribe(content):
    # get data from socket
    topic = str(content['topic'])

    # get advertised topics
    advertised_topics = get_advertised()

    # add topic to subscriptions if it is correct
    print("Subscribing...", topic, flush=True)
    if topic in advertised_topics:
        if topic not in subscribed:
            subscribed.append(topic)
            consumer.subscribe(subscribed)
    emit('subscribed', {'data': subscribed})
    print(subscribed, flush=True)
    print(consumer.subscription(), flush=True)


# Unsubscribe to topic
@socketio.on('unsubscribe')
def unsubscribe(content):
    # get data from socket
    topic = str(content['topic'])

    # remove topic from subscriptions if it exists
    print("Unsubscribing...", topic, flush=True)
    if topic in subscribed:
        subscribed.remove(topic)
        consumer.unsubscribe()
        consumer.subscribe(subscribed)
    emit('subscribed', {'data': subscribed})
    print(subscribed, flush=True)


# Get advertised topics
@socketio.on('advertised')
def advertised():
    result = get_advertised()
    print("Advertising... ", result, flush=True)
    emit('advertised', {'topics': result})


# Get new events under subscribed topics
@socketio.on('update')
def updates():
    if subscribed:
        try:
            # Retrieve events
            for m in consumer:
                print(m, flush=True)
                emit('notified', m.value)
            consumer.commit()
        except Exception as e:
            print(e)


# get list of advertised topics
def get_advertised():
    advertised_topics = consumer.topics()
    result = []
    for value in advertised_topics:
        if value.isdigit():
            result.append(value)
    return result


if __name__ == '__main__':
    sleep(10)
    # app.run(host="0.0.0.0", port=8000)
    port = os.environ.get('PORT')
    socketio.run(app, host='0.0.0.0', port=port)
