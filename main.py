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

class Post:
    def __init__(self, m):
        self.id = m['id']
        self.url = m['url']
        self.title = m['title']
        self.content = m['content']
        self.time = datetime.datetime.fromisoformat(m['time'])

@app.route('/')
def index() -> str:
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        posts = conn.execute('select * from posts').fetchall()
    posts = map(Post, posts)
    return flask.render_template('main.html', posts=posts)

@app.route('/newComment', methods=['POST'])
def newComment():
    author = flask.request.form.get('author')
    message = flask.request.form.get('message')
    time = datetime.datetime.now()
    post_id = int(flask.request.form.get('post_id'))
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('insert into comments (author, content, time, post_id) values (?, ?, ?, ?)', (author, message, time, post_id))
        post_url = conn.execute('select url from posts where id = ?', (post_id,)).fetchone()[0]
    return flask.redirect('/post/'+post_url)

@app.route('/post/<url>')
def showPost(url):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        posts = conn.execute('select * from posts where url = ?', (url,)).fetchall()
    if len(posts) == 0:
        flask.abort(404)
    post = Post(posts[0])
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        comments = conn.execute('select author, content, time from comments where post_id = ?', (post.id,)).fetchall()
    comments = map(Comment, comments)
    return flask.render_template('post.html', post=post, comments=comments)

@app.route('/post/new', methods=['GET'])
def newPostPage():
    return flask.render_template('newPost.html')

@app.route('/post/new', methods=['POST'])
def newPost():
    title = flask.request.form.get('title')
    content = flask.request.form.get('content')
    url = flask.request.form.get('url')
    time = datetime.datetime.now()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('insert into posts (url, title, content, time) values (?, ?, ?, ?)', (url, title, content, time))
    return flask.redirect('/post/'+url)

if __name__ == "__main__":
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                time TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL REFERENCES posts(id),
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                time TEXT NOT NULL
            )
        """)
    app.run(debug=True)