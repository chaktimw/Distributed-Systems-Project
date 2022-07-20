import pymongo
from database import database_tools

publisher_name = "cheap_shark"


def publish(data):
    counter = data['counter']
    raw_data = data['raw_data']
    raw_game = raw_data[counter]
    price = raw_game['salePrice']
    title = raw_game['title']
    game = {
        'title': title,
        'price': price
    }

    database_tools.add_event(game)

    filters = database_tools.get_publisher_topics(publisher_name)
    result = []
    for x in filters:
        filter_price = int(x)
        if int(float(price)) <= filter_price:
            database_tools.update_filter(x, game)
            result.append(filter_price)
    return (title, price, result)


def get_advertised():
    result = database_tools.get_publisher_topics(publisher_name)
    if result == -1:
        database_tools.add_publisher(publisher_name)
        result = database_tools.get_publisher_topics(publisher_name)
    return result


def advertise(value):
    current_topics = database_tools.get_publisher_topics(publisher_name)

    if value not in current_topics:
        database_tools.add_filter(value)
        result = database_tools.update_publisher(publisher_name, [value])
        if result == -1:
            return ""
        return result
    else:
        return ""


def deadvertise(value):
    current_topics = database_tools.get_publisher_topics(publisher_name)
    if value in current_topics:
        database_tools.remove_filter(value)
        result = database_tools.update_publisher_remove(publisher_name, value)
        return result
    else:
        return current_topics
