'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request

from datetime import datetime


try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green", "system"), to=int(room_id))

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red", "system"), to=int(room_id))

# send message event handler
@socketio.on("send")
def send(username, message, room_id, rname):
    db.store_message(username, rname, message)
    emit("incoming", (message, '', username), to=room_id)

    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

    if room_id is not None:
        room.join_room(sender_name, room_id)
        join_room(room_id)
        emit("incoming", (f"{sender_name} has joined the room.", "green", "system"), to=room_id, include_self=False)
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green", "system"))
    else:
        room_id = room.create_room(sender_name, receiver_name)
        join_room(room_id)
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green", "system"), to=room_id)

    last_seen = db.get_last_seen(sender_name, receiver_name)
    chat_history = db.get_chat_history(sender_name, receiver_name, last_seen)
    for msg, sender in chat_history:
        color = 'blue' if sender == sender_name else 'green'
        emit("incoming", (msg, color, sender), to=room_id)
    
    # Clear chat history after sending messages
    db.clear_chat_history(sender_name, receiver_name, last_seen)

    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red", "system"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)
    db.update_last_seen(username, username, datetime.now())
