import datetime
import flask
import sqlite3
app = flask.Flask(__name__)
DB_FILE = "comments.db"

@app.route('/')
def index() -> str:
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        comments = conn.execute('select author, content from comments').fetchall()
    return flask.render_template('template.html', comments=comments)

@app.route('/new', methods=['POST'])
def newComment():
    author = flask.request.form.get('author')
    message = flask.request.form.get('message')
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('insert into comments (author, content) values (?, ?)', (author, message))
    return flask.redirect('/')

if __name__ == "__main__":
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
    app.run(debug=True)