from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import time
import pose as pm
import threading
import pyttsx3

app = Flask(__name__)

# Initialize Mediapipe Pose Detector
detector = pm.PoseDetector()
cap = cv2.VideoCapture(0)  # Default to webcam

count = 0
dir = 0
pTime = 0
feedback = ""

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

def speak_feedback(feedback):
    engine.say(feedback)
    engine.runAndWait()

def schedule_feedback():
    global feedback
    if feedback:
        speak_feedback(feedback)
    threading.Timer(5.0, schedule_feedback).start()

schedule_feedback()

def process_frame():
    global count, dir, pTime, feedback
    success, img = cap.read()
    if not success:
        return None, ""
    
    img = cv2.resize(img, (990, 640))
    img = detector.findPose(img)
    lmList = detector.findPosition(img, False)
    
    if lmList:
        angle = detector.findAngle(img, 23, 25, 27)
        angle2 = detector.findAngle(img, 24, 26, 28)
        
        per = np.interp(angle, (77, 172), (100, 0))
        bar = np.interp(angle, (77, 172), (100, 550))
        
        feedback = ""
        if angle < 70:
            feedback = f"Bend less by {int(70 - angle)} degrees."
        elif angle > 110:
            feedback = f"Bend more by {int(angle - 110)} degrees."
        else:
            feedback = "Good form! You are perfect."
        
        torso_angle = detector.findAngle(img, 11, 23, 25)
        if torso_angle < 160:
            feedback += " Torso leaning forward! Straighten your back."
        elif torso_angle > 200:
            feedback += " Torso leaning backward! Lean slightly forward."
        
        if per == 100 and dir == 1:
            count += 0.5
            dir = 0
        if per == 0 and dir == 0:
            count += 0.5
            dir = 1
        
        cv2.putText(img, feedback, (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.rectangle(img, (875, 100), (900, 550), (0, 255, 0), 3)
        cv2.rectangle(img, (875, int(bar)), (900, 550), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(per)}%', (875, 75), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 4)
        cv2.rectangle(img, (0, 450), (150, 550), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (45, 520), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)
    
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes(), feedback

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            frame, _ = process_frame()
            if frame:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_feedback')
def get_feedback():
    _, current_feedback = process_frame()
    return jsonify({'feedback': current_feedback})

if __name__ == '__main__':
    app.run(debug=True)
