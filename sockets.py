from flask_socketio import emit
from extensions import socketio
from flask_socketio import emit, join_room, leave_room
import jwt
import os
from flask import request


@socketio.on('disconnect')
def handle_disconnect(reason=None):
    print('Client disconnected')

@socketio.on('connect')
def handle_connect(auth):
    token = None
    if auth and 'token' in auth:
        token = auth['token']
    else:
        token = request.args.get('token')

    if not token:
        print('Connection rejected: No token provided')
        return False

    try:
        jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        print('Client connected (authenticated)')
        emit('connection_response', {'message': 'Connected to server successfully'})
    except jwt.InvalidTokenError:
        print('Connection rejected: Invalid token')
        return False

@socketio.on_error_default
def default_error_handler(e):
    print(f'WebSocket error occurred: {str(e)}')


@socketio.on('send_message')
def handle_send_message(data):
    print(f"Message received: {data}")
    emit('receive_message', {
        'user': data.get('user', 'Anonymous'),
        'message': data.get('message', '')
    }, broadcast=True)


@socketio.on('typing_indicator')
def handle_typing(data):
    emit('user_typing', {
        'user': data.get('user', 'Anonymous')
    }, broadcast=True, include_self=False)
    
@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    join_room(room)
    print(f"Client joined room: {room}")
    emit('room_notification', {'message': f'You joined room {room}'}, room=room)


@socketio.on('leave_room')
def handle_leave_room(data):
    room = data.get('room')
    leave_room(room)
    print(f"Client left room: {room}")


@socketio.on('send_room_message')
def handle_send_room_message(data):
    room = data.get('room')
    print(f"Room message in {room}: {data}")
    emit('receive_message', {
        'user': data.get('user', 'Anonymous'),
        'message': data.get('message', '')
    }, room=room)