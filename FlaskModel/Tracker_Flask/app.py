from flask import Flask, Response, render_template
import cv2
import practice3  # Import your existing script

app = Flask(__name__)

# Initialize the video capture from `practice3.py`
def generate_frames():
    while True:
        img, feedback_text = practice3.test2()  # Call the function to process frames
        frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR (OpenCV format)
        ret, buffer = cv2.imencode('.jpg', frame)  # Encode image as JPEG
        frame = buffer.tobytes()
        
        # Yield the frame with multipart encoding for live streaming
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')  # Create an HTML page to display video

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
