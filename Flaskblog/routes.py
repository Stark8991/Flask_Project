import os
import secrets
from PIL import Image
from Flaskblog import app, flask_bcrypt, db, mail
from flask import render_template, url_for, redirect, flash, request, abort
from Flaskblog.form import (RegistrationForm, LoginForm, PostForm, Profile, RequestResetForm,
                            reset_password_form)
from Flaskblog.models import User, Post
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    Posts = Post.query.order_by(
        Post.date_posted.desc()).paginate(page=page, per_page=4)

    return render_template('home.html', title='Fling', Posts=Posts)


@app.route('/about')
def about():
    return render_template('about.html', title='Fling-about')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and flask_bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid credintials', 'danger')
    return render_template('login.html', form=form, title='Login in')


@app.route('/register', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = flask_bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created', 'success')
        return redirect(url_for('login'))
    return render_template('RegistrationForm.html', form=form, title='Sign Up')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required
def account():
    return render_template('account.html', title=current_user.username)


@app.route('/Fling', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.text_area.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Posted.', 'success')
        return redirect(url_for('home'))
    return render_template('Create_Post.html', form=form, legend="New Post")


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('Post.html', Post=post)


@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    else:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('home'))


def save_picture(file):
    hex_code = secrets.token_hex(12)
    file_name, file_type = os.path.splitext(file.filename)
    new_file_name = hex_code + file_type
    file_path = os.path.join(
        app.root_path, 'static\profile_pic', new_file_name)

    size = (1280, 720)
    i = Image.open(file)
    i.thumbnail(size)
    i.save(file_path)
    return new_file_name


@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = Profile()
    if form.validate_on_submit():
        if form.picture.data:
            image = save_picture(form.picture.data)
            current_user.image_file = image
        db.session.commit()
        flash('Account Updated!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', form=form)


@app.route('/user_profile/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    length = len(user.posts)
    return render_template('user_profile.html', user=user, Total_Post=length)


def send_reset_email(user):
    token = user.get_set_token()
    msg = Message('Password Reset Request',
                  sender="from@example.com", recipients=[user.email])
    msg.body = f'''
    To reset your password follow this link:
    {url_for('reset_token', token = token, _external = True)}

    If you did not make this request then simply ignore this email and no changes will be made

    '''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def password_reset_form():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Request completed. Check your email ', 'success')
        return redirect(url_for('login'))
    return render_template('request_reset_form.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('Reset token is expired', 'Warning')
        return redirect(url_for('login'))
    form = reset_password_form()
    if form.validate_on_submit():
        hash_password = flask_bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hash_password
        db.session.commit()
        flash('Your Password has been updated', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
