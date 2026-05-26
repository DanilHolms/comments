import datetime
import flask
import sqlite3

app = flask.Flask(__name__)
DB_FILE = "comments.db"

class Comment:
    def __init__(self, m):
        self.author = m['author']
        self.content = m['content']
        self.time = datetime.datetime.fromisoformat(m['time'])

@app.route('/')
def index() -> str:
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        comments = conn.execute('select author, content, time from comments').fetchall()
    comments = map(Comment, comments)
    return flask.render_template('template.html', comments=comments)

@app.route('/new', methods=['POST'])
def newComment():
    author = flask.request.form.get('author')
    message = flask.request.form.get('message')
    time = datetime.datetime.now()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('insert into comments (author, content, time) values (?, ?, ?)', (author, message, time))
    return flask.redirect('/')

if __name__ == "__main__":
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                time TEXT NOT NULL
            )
        """)
    app.run(debug=True)