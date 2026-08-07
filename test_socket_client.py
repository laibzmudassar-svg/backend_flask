import socketio
import time

sio = socketio.Client()

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIxLCJlbWFpbCI6ImxhaWJ6QGdtYWlsLmNvbSIsImV4cCI6MTc4NTc5OTg3Mn0.YMPgIsIW-Lo8HTi0MNbG8EUzUr77hPf24hjsfLYC1Eo"

@sio.event
def connect():
    print('✅ Connected to server (authenticated)!')

@sio.event
def connection_response(data):
    print('Server says:', data)

@sio.event
def connect_error(data):
    print('🚫 Connection rejected by server:', data)

@sio.event
def disconnect():
    print('❌ Disconnected from server')

sio.connect('http://127.0.0.1:5000', auth={'token': TOKEN})
time.sleep(2)
sio.disconnect()