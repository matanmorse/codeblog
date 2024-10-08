from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db, create_app
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)
@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.hash, password):
        flash('Please check your login details and try again')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
    

    # if the rest is true the user has the correct credentials and should be logged in
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template("signup.html")

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email').lower()
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if not email or not name or not password:
        flash('Please enter all fields')
        return redirect(url_for('auth.signup'))

     # if a user is found, we want to redirect back to signup page so user can try again
    if user:
        flash('''Email address already exists. Go to <a href = "/login">login page</a>.''')

        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, hash=generate_password_hash(password, method='sha256'), admin=False)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # automatically login user once registered
    login_user(new_user)

    return redirect(url_for('main.profile'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

