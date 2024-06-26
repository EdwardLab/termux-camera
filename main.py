from flask import Flask, render_template_string
from flask_socketio import SocketIO
import subprocess
import os
import base64
import io

app = Flask(__name__)
socketio = SocketIO(app)
latest_frame = None

def capture_frame():
    global latest_frame
    result = subprocess.run(['termux-camera-photo', '-c', '0', 'camera.jpg'], capture_output=True)
    if result.returncode == 0 and os.path.exists('camera.jpg'):
        with open('camera.jpg', 'rb') as file:
            latest_frame = file.read()

@app.route('/')
def index():
    return render_template_string('''
        <!doctype html>
        <title>Camera Stream</title>
        <h1>Camera Stream</h1>
        <img id="video_feed" width="100%">
        <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
        <script>
            var socket = io();
            socket.on('frame', function(data) {
                var img = document.getElementById('video_feed');
                img.src = 'data:image/jpeg;base64,' + data;
            });
            setInterval(function() {
                socket.emit('request_frame');
            }, 90);  // Request a new frame
        </script>
    ''')

@socketio.on('request_frame')
def handle_request_frame():
    capture_frame()
    if latest_frame:
        encoded_frame = base64.b64encode(latest_frame).decode('utf-8')
        socketio.emit('frame', encoded_frame)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5510)
