from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import time
import pose as pm
import pyttsx3
import threading

app = Flask(__name__)

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)

# Global variables
cap = None
detector = pm.PoseDetector()
count = 0
dir = 0
pTime = 0
feedback = ""  # Global variable to store feedback

# Function to speak feedback
def speak_feedback(feedback):
    engine.say(feedback)
    engine.runAndWait()

# Function to schedule voice feedback every 5 seconds
def schedule_feedback():
    global feedback
    if feedback:  # Only speak if there is feedback
        speak_feedback(feedback)
    threading.Timer(5.0, schedule_feedback).start()  # Schedule again after 5 seconds

# Video accessing
def camselect(cam=1, file1=None):
    global cap
    if cam:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(file1)

camselect()
schedule_feedback()

def generate_frames():
    global count, dir, pTime, feedback
    while True:
        success, img = cap.read()
        if not success:
            break
        else:
            # Sizing the screen
            img = cv2.resize(img, (990, 640))  # width, height
            
            img = detector.findPose(img)
            lmList = detector.findPosition(img, False)
            
            if len(lmList) != 0:
                angle = detector.findAngle(img, 23, 25, 27)  # Left leg
                angle2 = detector.findAngle(img, 24, 26, 28)  # Right leg
                
                # Calculate percentage of the lunge
                per = np.interp(angle, (77, 172), (100, 0))
                bar = np.interp(angle, (77, 172), (100, 550))
                
                # Feedback based on angles
                feedback = ""
                if angle < 70:  # Too bent
                    ang = 70 - angle
                    feedback = f"Bend less by {int(ang)} degrees."
                elif angle > 110:  # Not bent enough
                    ang2 = angle - 110
                    feedback = f"Bend more by {int(ang2)} degrees."
                else:
                    feedback = "Good form! You are perfect."
                
                # Additional feedback for torso alignment
                torso_angle = detector.findAngle(img, 11, 23, 25)  # Angle between shoulder, hip, and knee
                if torso_angle < 160:  # Torso leaning forward
                    feedback += " Torso leaning forward! Straighten your back."
                elif torso_angle > 200:  # Torso leaning backward
                    feedback += " Torso leaning backward! Lean slightly forward."
                
                # Count logic
                if per == 100:
                    if dir == 1:
                        count += 0.5
                        dir = 0
                if per == 0:
                    if dir == 0:
                        count += 0.5
                        dir = 1
                
                # Draw feedback on the screen
                cv2.putText(img, feedback, (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                
                # Draw the bar and percentage
                cv2.rectangle(img, (875, 100), (900, 550), (0, 255, 0), 3)
                cv2.rectangle(img, (875, int(bar)), (900, 550), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f'{int(per)}%', (875, 75), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 4)
                
                # Draw the count
                cv2.rectangle(img, (0, 450), (150, 550), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, str(int(count)), (45, 520), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)
            
            # Displaying FPS
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime

            cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            ret, buffer = cv2.imencode('.jpg', rgb)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', gif_url='/static/pose.gif')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/open_file', methods=['POST'])
def open_file():
    file1 = request.form['file']
    cam = 0
    camselect(cam, file1)
    return jsonify(success=True)

@app.route('/get_feedback', methods=['GET'])
def get_feedback():
    global feedback
    return jsonify(feedback=feedback)

if __name__ == '__main__':
    app.run(debug=True)
