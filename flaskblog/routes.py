from re import I
import secrets
import os
from turtle import title
from PIL import Image
from flask import redirect, render_template, url_for, flash, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post
from flaskblog import app, db, bcrypt
from flask_login import current_user, login_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def Home():
    page = request.args.get('page', default=1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('Home.html', posts=posts)

@app.route("/about")
def About():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET','POST'])
def Register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}.', 'success')
        return redirect(url_for('Login'))
    return render_template('register.html', title='Register', form = form)

@app.route("/login", methods=['GET','POST'])
def Login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') #we are using the get method instead of the ['key] 
            return redirect(next_page) if next_page else redirect(url_for('Home'))
        else:    
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form = form)

@app.route("/logout")
def Logout():
    logout_user();
    return redirect(url_for('Home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fin = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile-pics', picture_fin)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fin

@app.route("/account", methods=['GET','POST'])
@login_required
def Account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!')
        return redirect(url_for('Account'))
    image_file = url_for('static', filename=('profile-pics/' + current_user.image_file))
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET','POST'])
@login_required
def New_Post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post has been created!', 'success')
        return redirect(url_for('Home'))
    return render_template('create_post.html', title='New Post', form=form)

@app.route("/post/<int:post_id>")
def View_Post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post, legend = 'Create Post')

@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def Update_Post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    else:
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash('Your Post has been updated!', 'success')
            return redirect(url_for('View_Post', post_id=post.id))
        elif request.method == 'GET':    
            form.title.data = post.title
            form.content.data = post.content
        return render_template('create_post.html', title='Update post', form = form, post=post, legend = 'Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def Delete_Post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Your Post has been Deleted!', 'success')
        return redirect(url_for('Home'))

@app.route("/user/<string:username>")
def User_Post(username):
    page = request.args.get('page', default=1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)