import pymongo

# MongoDB database credentials
username = "Server"
password = "SbLyWirFroOagjoB"

# Connect to database
client = pymongo.MongoClient("mongodb+srv://Server:" +
                             password +
                             "@projectdatabase.9waxj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.myFirstDatabase  # db reference


# Publisher methods
def add_publisher(publisher):
    """
    add_publisher adds publisher to collection of publishers
    :param publisher: Name of publisher
    :return: None
    """
    # Get publishers collection
    publishers = db['publishers']

    # Add name to collection
    entry = {
        "publisher": publisher,
        "advertised": []
    }
    publishers.insert_one(entry)


def get_publisher_topics(publisher):
    """
    get_publisher gets publisher entry from collection of publishers if it exists
    :param publisher: Name of publisher
    :return: list of publisher's advertised topics, or -1 if it does not exist in the database
    """
    # Get publishers collection
    publishers = db['publishers']

    # Setup query details
    query = {'publisher': publisher}
    filters = {'_id': False, 'publisher': 0}

    # Get specified publisher data if it exists
    result = list(publishers.find(query, filters))

    if len(result) > 0:
        return result[0]['advertised']
    else:
        return -1


def update_publisher(publisher, data):
    """
    update_publisher updates the specified publisher entry in the publisher collection
    :param publisher: Name of publisher
    :param data: new data
    :return: 1 if successful, or -1 if it does not exist in the database
    """
    # Get publishers collection
    publishers = db['publishers']
    query = {'publisher': publisher}

    # Get specified publisher's topics, if publisher exists
    topics = get_publisher_topics(publisher)
    if topics == -1:
        return -1

    # Add new values
    new_topics = topics + data
    val = {"$set": {"advertised": new_topics}}

    # Add data to topics and push to database
    publishers.update_one(query, val)

    return get_publisher_topics(publisher)


def update_publisher_remove(publisher, data):
    """
    update_publisher_remove removes data value from publisher entry in collections
    :param publisher: Name of publisher
    :param data: data to be removed
    :return: 1 if successful, or -1 if it does not exist in the database
    """
    # Get publishers collection
    publishers = db['publishers']
    query = {'publisher': publisher}

    # Get specified publisher's topics, if publisher exists
    topics = get_publisher_topics(publisher)
    if topics == -1 or data not in topics:
        return -1

    # Add new values
    topics.remove(data)
    val = {"$set": {"advertised": topics}}

    # Add data to topics and push to database
    publishers.update_one(query, val)

    return get_publisher_topics(publisher)


def remove_publisher(publisher):
    """
    remove_publisher removes publisher from publishers collection
    :param publisher: Name of publisher
    :return: None
    """
    # Get publishers collection
    publishers = db['publishers']
    query = {"publisher": publisher}

    publishers.delete_one(query)


# Subscriber methods
def add_subscriber(subscriber):
    """
    add_subscriber adds subscriber to collection of subscribers
    :param subscriber: ID of subscriber
    :return: None
    """
    # Get subscribers collection
    subscribers = db['subscribers']

    # Add name to collection
    entry = {
        "subscriber": subscriber,
        "subscribed_topics": []
    }
    subscribers.insert_one(entry)


def get_subscriber_topics(subscriber):
    """
    get_subscriber gets subscriber entry from collection of subscribers if it exists
    :param subscriber: int id of subscriber
    :return: dictionary containing subscriber details, or -1 if it does not exist in the database
    """
    # Get subscribers collection
    subscribers = db['subscribers']

    # Setup query details
    query = {'subscriber': subscriber}
    filters = {'_id': False, 'subscriber': 0}

    # Get specified publisher data if it exists
    result = list(subscribers.find(query, filters))

    if len(result) > 0:
        return result[0]['subscribed_topics']
    else:
        return -1


def update_subscriber(subscriber, data):
    """
    update_subscriber updates the specified subscriber entry in the subscriber collection
    :param subscriber: int ID of subscriber
    :param data: new data
    :return: 1 if successful, or -1 if it does not exist in the database
    """
    # Get subscriber collection
    subscribers = db['subscribers']
    query = {'subscriber': subscriber}

    # Get specified subscriber's topics, if subscriber exists
    topics = get_subscriber_topics(subscriber)

    # Add new values
    new_topics = topics + data
    val = {"$set": {"subscribed_topics": new_topics}}

    # Add data to topics and push to database
    subscribers.update_one(query, val)

    return 1


def update_subscriber_remove(subscriber, data):
    """
    update_subscriber_remove removes data value from subscriber entry in collections
    :param publisher: Name of subscriber
    :param data: data to be removed
    :return: 1 if successful, or -1 if it does not exist in the database
    """
    # Get subscribers collection
    subscribers = db['subscribers']
    query = {'subscriber': subscriber}

    # Get specified subscriber's topics, if subscriber exists
    topics = get_subscriber_topics(subscriber)
    if topics == -1 or data not in topics:
        return -1

    # Add new values
    topics.remove(data)
    val = {"$set": {"subscribed_topics": topics}}

    # Add data to topics and push to database
    subscribers.update_one(query, val)

    return get_subscriber_topics(subscriber)


def remove_subscriber(subscriber):
    """
    remove_subscriber removes subscriber from subscribers collection
    :param subscriber: int ID of subscriber
    :return: None
    """
    # Get subscribers collection
    subscribers = db['subscribers']
    query = {"subscriber": subscriber}

    subscribers.delete_one(query)


# filtered messages collection methods
def add_filter(events_filter):
    """
    add_filter adds filter to collection of filters
    :param events_filter: str name of filter
    :return: None
    """
    # Get filters collection
    filters = db['filters']

    # Add name to collection
    entry = {
        "filter": events_filter,
        "filtered_events": []
    }
    filters.insert_one(entry)


def get_filtered_events(events_filter):
    """
    get_filtered_events gets all the filtered events from the filters collection
    :param events_filter: str name of filter
    :return: list of dictionaries, or -1 if it does not exist in the database
    """
    # Get subscribers collection
    filters = db['filters']

    # Setup query details
    query = {'filter': events_filter}
    query_filters = {'_id': False, 'filter': 0}

    # Get specified filter's events if it exists
    result = list(filters.find(query, query_filters))

    if len(result) > 0:
        return result[0]['filtered_events']
    else:
        return -1


def update_filter(events_filter, data):
    """
    update_filter updates the specified filter entry in the filters collection
    :param events_filter: str name of filter
    :param data: new data
    :return: 1 if successful, or -1 if it does not exist in the database
    """
    # Get filter collection
    filters = db['filters']
    query = {'filter': events_filter}

    # Get specified filter's events, if filter exists
    events = get_filtered_events(events_filter)

    # Add new values
    new_events = events + [data]
    val = {"$set": {"filtered_events": new_events}}

    # Add events to filter and push to database
    filters.update_one(query, val)

    return 1


def remove_filter(events_filter):
    """
    remove_filter removes filter from filters collection
    :param events_filter: str name of filter
    :return: None
    """
    # Get filters collection
    filters = db['filters']
    query = {"filter": events_filter}

    filters.delete_one(query)


# unfiltered messages collection methods
def add_event(event):
    """
    add_event adds event to the collection of unfiltered messages
    :param event: unfiltered message
    :return: None
    """
    # Get events collection
    events = db['events']

    events.insert_one(event)


def get_event(event):
    """
    get_event gets the specified event entry from the collection of unfiltered messages
    :param event: unfiltered message
    :return: list of dictionaries, or -1 if it does not exist in the database
    """
    # Get events collection
    events = db['events']

    # Setup query details
    query = event
    query_filters = {'_id': False, 'filter': 0}

    # Get specified filter's events if it exists
    result = list(events.find(query, query_filters))

    if len(result) > 0:
        return result[0]
    else:
        return -1


# API tracker methods
def add_tracker():
    """
    add_tracker adds a collection to DB that tracks the number of titles published
    :return: None
    """
    # Get tracker collection
    tracker = db['tracker']

    # Add name to collection
    entry = {
        "tracked": "titles_published",
        "counter": 0
    }
    tracker.insert_one(entry)


def get_tracker():
    """
    get_tracker gets current count of published titles in tracker collection
    :return: int, or -1 if non-existent
    """
    # Get tracker collection
    tracker = db['tracker']

    # Setup query details
    query = {'tracked': "titles_published"}
    filters = {'_id': False, 'tracked': 0}

    # Get specified tracker data if it exists
    result = list(tracker.find(query, filters))
    if len(result) > 0:
        counter = result[0]['counter']
        return counter
    else:
        add_tracker()
        return 0


def update_tracker():
    """
    update_tracker increments current count of published titles in tracker collection by 1
    :return: 1 if successful, or -1 if it does not exist in the database
    """
    # Get tracker collection
    tracker = db['tracker']
    query = {'tracked': "titles_published"}

    # Get current count
    counter = get_tracker()
    if counter == -1:
        return -1

    # Increment counter
    val = {"$set": {"counter": counter + 1}}

    # push to database
    tracker.update_one(query, val)

    return 1
