from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

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
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        username_error = "Username not in database"
        password_error = "Password doesn't match our records"
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
           return render_template('login.html', username_error=username_error, password_error=password_error)
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""
        verify_error = ""
        existing_error = ""

        if len(username) == 0 or len(username) < 3 or len(username) > 20 or ' ' in username:
            username_error = "Not a valid username"
    
        if len(password) == 0 or len(password) < 3 or len(password) > 20 or ' ' in password:
            password_error = "Not a valid password"
    
        if verify != password:
            verify_error = "Passwords don't match"

        if existing_user:
            existing_error = "Username taken"

        if username_error or password_error or verify_error or existing_user:
            return render_template('register.html', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error, existing_error=existing_error)  
            
        elif not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')                
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

   
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
            post = str(new_blog.id)
            return redirect('/blog?id=' + post)
    return render_template('new_post.html')
      
@app.route("/blog", methods=['GET', 'POST'])
def blog():
    posts = Blog.query.all()
    authors = User.query.all()
    id = request.args.get('id')
    userID = request.args.get('user')
   
    
    if id:
        unique_id = Blog.query.filter_by(id=id).first()
        return render_template("single_post.html", post=unique_id, author=userID)
    elif userID:
        author = User.query.filter_by(username=userID).first()
        owner = Blog.query.filter_by(owner_id=author.id).all()
        return render_template("singleUser.html", posts=owner)
    else:
        return render_template("blog.html", posts=posts)
        
    



if __name__ == '__main__':
    app.run()