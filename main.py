from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:NewPass@localhost:8889/Blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '123456'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner.id')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/')
        else:
           flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            #TODO - better user response
            return'<h1>duplicate user</h1>'
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

   
@app.route("/newpost", methods=['POST', 'GET'])
def blog_entries():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        title_error = ""
        body_error = ""
        if len(blog_title) == 0:
            title_error = "Title is required"
        if len(blog_body) == 0:
            body_error = "Body is required"
        if title_error or body_error:
            return render_template('new_post.html', title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            post = new_blog.id
            return redirect('/blog?id=' + str(post))
    return render_template('new_post.html')
      
@app.route("/blog", methods=['GET', 'POST'])
def blog():

    posts = Blog.query.all()
    id = request.args.get('id')
    unique_id = Blog.query.filter_by(id=id).first()
    if not unique_id:
        return render_template("blog.html", posts=posts)
    else:
        return render_template("single_post.html", post=unique_id)




if __name__ == '__main__':
    app.run()