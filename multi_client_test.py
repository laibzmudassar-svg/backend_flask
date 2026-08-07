import socketio
import time
import threading

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIyLCJlbWFpbCI6Im1pbmFAZ21haWwuY29tIiwiZXhwIjoxNzg1ODAxNDgxfQ.1E8Yvo7Au5hPbWhr8NYfI5dxehUZV36L6tc-Y2f5ZtM"

def run_client(name):
    sio = socketio.Client()

    @sio.event
    def connect():
        print(f'[{name}] ✅ Connected')
        sio.emit('join_room', {'room': 'chat_room_101'})

    @sio.event
    def room_notification(data):
        print(f'[{name}] 🚪 {data}')

    @sio.event
    def receive_message(data):
        print(f'[{name}] 📩 Received: {data}')

    sio.connect('http://127.0.0.1:5000', auth={'token': TOKEN})
    time.sleep(1)

    if name == 'Client-A':
        sio.emit('send_room_message', {
            'room': 'chat_room_101',
            'user': name,
            'message': 'Hi everyone in the room!'
        })

    time.sleep(2)
    sio.disconnect()
    print(f'[{name}] ❌ Disconnected')


t1 = threading.Thread(target=run_client, args=('Client-A',))
t2 = threading.Thread(target=run_client, args=('Client-B',))

t1.start()
time.sleep(0.5)
t2.start()

t1.join()
t2.join()