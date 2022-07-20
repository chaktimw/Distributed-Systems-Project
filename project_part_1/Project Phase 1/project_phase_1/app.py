from flask import Flask, send_from_directory, render_template, request, redirect, escape
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'test_database',
    'host': 'mongo',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)


class Comment(db.Document):
    name = db.StringField(max_length=120)
    content = db.StringField()


@app.route('/', methods=['GET'])
def homepage():
    comments = ""
    for post in Comment.objects:
        comments += "<b>Name: </b>" + post.name + " <b>Comment: </b>" + post.content + "<br>"
    return render_template('index.html', Comments=comments)


@app.route('/comment', methods=['POST'])
def receive_data():
    data = request.form
    Comment(name=escape(data['name']), content=escape(data['comment'])).save()
    return redirect('/')


@app.route('/static/<path:filename>')
def jscript(filename):
    return render_template('static', filename)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
