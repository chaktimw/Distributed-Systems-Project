import pymongo
from database import database_tools
import requests
import json


def test_publishers():
    publisher_name = "cheap_shark"
    
    # Test add
    database_tools.add_publisher(publisher_name)

    # # Test update
    # print(database_tools.get_publisher_topics(publisher_name))
    # database_tools.update_publisher(publisher_name, ['bus', 'lost', 'bad'])
    #
    # # Test remove
    # database_tools.remove_publisher(publisher_name)
    #
    # print(database_tools.get_publisher_topics(publisher_name))


def test_subscribers():
    subscriber_id = 55

    # Test add
    database_tools.add_subscriber(subscriber_id)

    # Test update
    print(database_tools.get_subscriber_topics(subscriber_id))
    database_tools.update_subscriber(subscriber_id, ['Movies', 'Romance'])

    # Test remove
    database_tools.remove_subscriber(subscriber_id)

    print(database_tools.get_subscriber_topics(subscriber_id))


def test_filters():
    events_filter = "Games"
    r = requests.get("https://www.cheapshark.com/api/1.0/deals?upperPrice=5")
    data = json.loads(r.content)
    current_game = 0

    # Test add
    database_tools.add_filter(events_filter)

    # Test update
    print(database_tools.get_filtered_events(events_filter))
    database_tools.update_filter(events_filter, data[current_game])
    current_game += 1
    print(database_tools.get_filtered_events(events_filter))
    database_tools.update_filter(events_filter, data[current_game])

    # Test remove
    # database_tools.remove_subscriber(subscriber_id)

    print(database_tools.get_filtered_events(events_filter))


def test_tracker():
    # database_tools.add_tracker()
    print(database_tools.get_tracker())
    database_tools.update_tracker()
    print(database_tools.get_tracker())
