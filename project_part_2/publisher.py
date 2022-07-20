from time import sleep
from json import dumps
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import requests


# get API data
def get_data():
    r = requests.get("https://www.cheapshark.com/api/1.0/deals?")
    content = json.loads(r.content)
    return content


# Topics and game data
topics = ['5', '10', '20']        # contains price range topics advertised by this publisher
topic_list = []                   # contains list of NewTopic
raw_data = get_data()             # list of dictionaries (each dict is a game) from API

# Wait until kafka broker containers have been completely initialized
sleep(20)

# Admin (add partitions)
bootstrap_servers=['kafka-1:9092', 'kafka-2:9092', 'kafka-3:9092']
admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
for topic in topics:
    topic_list.append(NewTopic(name=topic, num_partitions=3, replication_factor=1))
try:
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
except Exception as e:
    print(e)

# Create kafka producer object
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    api_version=(0, 10, 1),
    value_serializer=lambda x: dumps(x).encode('utf-8'),
    # partitioner="all_partitions"
)

# Publish empty events to establish topics
# for topic in topics:
#     producer.send(str(topic), value={})

# Publish an event to kafka broker network every release_rate seconds
release_rate = 10
for j in range(len(raw_data)):

    # get game data from API
    raw_game = raw_data[j]
    price = raw_game['salePrice']
    title = raw_game['title']
    game = {
        'title': title,
        'price': price
    }

    # if price of game falls under one of the listed topic prices
    max_price = int(topics[len(topics) - 1])
    int_price = int(float(price))
    if int_price < max_price:

        # determine the topic this game falls under
        section = 0
        topic = int(topics[section])
        # print(topic, flush=True)
        while int_price > topic:
            section += 1
            topic = int(topics[section])

        # publish event under specified topic
        print("Publishing event... ", "PriceTopic =", topic, game, flush=True)
        producer.send(str(topic), value=game)

    # sleep
    sleep(release_rate)

# when loop is complete, print message
print("out of events to publish...", flush=True)