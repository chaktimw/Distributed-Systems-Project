import pymongo

client = pymongo.MongoClient("mongodb://mongo:27017")
db = client.myFirstDatabase


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
        "advertised": [],
        "counter": 0
    }
    publishers.insert_one(entry)


def get_publisher(publisher):
    """
    get_publisher gets publisher entry from collection of publishers if it exists
    :param publisher: Name of publisher
    :return: publisher's data, or -1 if it does not exist in the database
    """
    # Get publishers collection
    publishers = db['publishers']

    # Setup query details
    query = {'publisher': publisher}
    filters = {'_id': False, 'publisher': 0}

    # Get specified publisher data if it exists
    result = list(publishers.find(query, filters))

    if len(result) > 0:
        return result[0]
    else:
        return -1


def update_publisher(publisher, data, counter):
    """
    update_publisher updates the specified publisher entry in the publisher collection
    :param publisher: Name of publisher
    :param data: new data
    :param counter: API tracker
    :return: 1 if successful, or -1 if it does not exist in the database
    """
    # Get publishers collection
    publishers = db['publishers']
    query = {'publisher': publisher}

    # Get specified publisher's data, if publisher exists
    publisher_data = get_publisher(publisher)
    if publisher_data == -1:
        return -1
    topics = publisher_data['advertised']  # publisher's topics
    count = counter
    if count == -1:
        count = publisher_data['counter']   # keep current tracker value

    # Add new values
    new_topics = topics + data
    val = {"$set": {"advertised": new_topics, "counter": count}}

    # Add data to topics and push to database
    publishers.update_one(query, val)

    return get_publisher(publisher)


def update_publisher_remove(publisher, topic):
    """
    update_publisher_remove removes topic from publisher entry in collections
    :param publisher: Name of publisher
    :param topic: data to be removed
    :return: 1 if successful, or -1 if it does not exist in the database
    """
    # Get publishers collection
    publishers = db['publishers']
    query = {'publisher': publisher}

    # Get specified publisher's topics, if publisher exists
    publisher_data = get_publisher(publisher)
    if publisher_data == -1:
        return -1
    if topic not in publisher_data['advertised']:
        return {'advertised': "FUUUUUU"}

    # Add new values
    topics = publisher_data['advertised']
    topics.remove(topic)
    val = {"$set": {"advertised": topics}}

    # Add data to topics and push to database
    publishers.update_one(query, val)

    return get_publisher(publisher)


# Subscriber methods
def add_subscriber(subscriber):
    """
    add_subscriber adds subscriber to collection of subscribers
    :param subscriber: ID of subscriber
    :return: None
    """
    # Get subscribers collection
    subscribers = db['subscribers']

    # Create entry
    entry = {
        "subscriber": subscriber,
        "subscribed_topics": []
    }

    if get_subscriber_topics(subscriber) == -1:
        subscribers.insert_one(entry)  # add name to collection


def get_subscriber_topics(subscriber):
    """
    get_subscriber gets subscriber entry from collection of subscribers
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
    if topics == -1:
        return -1

    # Add new values
    new_topics = topics + data
    val = {"$set": {"subscribed_topics": new_topics}}

    # Add data to topics and push to database
    subscribers.update_one(query, val)

    return 1


def update_subscriber_remove(subscriber, data):
    """
    update_subscriber_remove removes data value from subscriber entry in collections
    :param subscriber: Name of subscriber
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

    # add filter if it does not exist
    if get_filtered_events(events_filter) == -1:
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


def get_all_filtered_events():
    """
    get_all_filtered_events gets all the filters from the filters collection
    :return: list of events, or -1 if none exist in the database
    """
    # Get subscribers collection
    filters = db['filters']

    # Setup query details
    query = {}
    query_filters = {'_id': False, 'filtered_events': 0}

    # Get all filters if they exist
    found_filters = []
    result = filters.find(query, query_filters)

    # convert to list of filters
    for value in result:
        found_filters.append(value['filter'])

    if len(found_filters) > 0:
        return found_filters
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
