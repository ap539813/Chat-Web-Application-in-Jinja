'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, session
from flask_socketio import SocketIO
import db
import secrets
from hashlib import sha256
import os
import hashlib
import uuid
import ssl


# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)


@app.before_request
def authenticate():
    """Authenticate the user for each request"""
    if 'token' not in session and request.endpoint not in ['login_user', 'index', 'login', 'static', 'logout', 'signup', 'user', 'signup_user']:
        abort(401)  # Unauthorized

# don't remove this!!
import socket_routes

def generate_token(username):
    """Generate a unique token for the user"""
    return str(uuid.uuid4()) + username

@app.route("/add_friend", methods=["POST"])
def add_friend():
    if 'username' not in session:
        abort(404)
    
    if not request.is_json:
        abort(404)
    print(request.json)
    username = request.json.get("username")
    friend_username = request.json.get("friend_username")
    if db.add_friend_request(username, friend_username):
        return "Friend request sent"
    else:
        return "Friend request already exists", 400
    

@app.route("/remove_friend", methods=["POST"])
def remove_friend():
    if 'username' not in session:
        abort(404)

    if not request.is_json:
        abort(404)
    
    username = request.json.get("username")
    friend_username = request.json.get("friend_username")
    
    if db.remove_friend(username, friend_username):
        return "Friend removed"
    else:
        return "Failed to remove friend", 400


@app.route("/approve_friend", methods=["POST"])
def approve_friend():
    if 'username' not in session:
        abort(404)
    
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    friend_username = request.json.get("friend_username")
    if db.approve_friend_request(username, friend_username):
        return "Friend request approved"
    else:
        return "Failed to approve friend request", 400

@app.route("/reject_friend", methods=["POST"])
def reject_friend():
    if 'username' not in session:
        abort(404)
    
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    friend_username = request.json.get("friend_username")
    if db.reject_friend_request(username, friend_username):
        return "Friend request rejected"
    else:
        return "Failed to reject friend request", 400

@app.route("/chat/<username>/<rname>")
def chat(username, rname):
    
    logged_in_user = username
    chat_history = db.get_chat_history(logged_in_user, rname)
    return chat_history

@app.route("/friend_requests")
def friend_requests():
    if 'username' not in session:
        abort(404)
    username = session['username']
    sent_requests, received_requests = db.get_friend_requests(username)
    return render_template("friend_requests.jinja", sent_requests=sent_requests, received_requests=received_requests, username=username)

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")


# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")
    salt = request.json.get("salt")
    user = db.get_user(username)
    
    if user is None:
        return "Error: User does not exist!"

    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    
    if user.password != hashed_password:
        return "Error: Password does not match!"

    db.set_user_online(username)  # Update online status

    session['username'] = username
    session['token'] = generate_token(username)

    return url_for('home', username=username)



@app.route("/logout")
def logout():
    if 'username' in session:
        db.set_user_offline(session['username'])
    
    session.clear()
    return render_template("index.jinja")


# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    
    username = request.json.get("username")
    password = request.json.get("password")
    salt = request.json.get("salt")
    role = request.json.get("role")  

    if db.get_user(username) is None:
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        db.insert_user(username, hashed_password, role)  # Adjust the method to accept role
        session['username'] = username
        session['token'] = generate_token(username)
        return url_for('home', username=username)
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if 'username' not in session:
        abort(404)

    if request.args.get("username") is None:
        abort(404)
    
    username = request.args.get("username")
    friend_list = db.get_friends(username)
    sent_requests, received_requests = db.get_friend_requests(username)
    return render_template("home.jinja", username=request.args.get("username"), sent_requests=sent_requests, received_requests=received_requests, friend_list=friend_list)

 
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) 
context.load_cert_chain('./certs/localhost.crt', './certs/localhost.key')
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=443, ssl_context=context, debug=True)
   
# if __name__ == '__main__':
#     ssl_args = {
#         'certfile': './certs/localhost.crt',
#         'keyfile': './certs/localhost.key'
#     }

#     # Create a listener
#     listener = eventlet.listen(('localhost', 8000))

#     # Wrap the listener with SSL
#     ssl_listener = eventlet.wrap_ssl(listener, **ssl_args, server_side=True)

#     # Use Eventlet to serve the application
#     wsgi.server(ssl_listener, app)
