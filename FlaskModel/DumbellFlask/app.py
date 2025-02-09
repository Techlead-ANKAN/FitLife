from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import base64
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

def detect_biceps(frame):
    """
    Detect biceps using MediaPipe Pose.
    """
    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Pose
    results = pose.process(rgb_frame)

    # Check if biceps are detected
    if results.pose_landmarks:
        # Get landmarks for left and right shoulders and elbows
        landmarks = results.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]

        # Draw landmarks on the frame
        h, w, _ = frame.shape
        for landmark in [left_shoulder, right_shoulder, left_elbow, right_elbow]:
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        return frame, True
    return frame, False

@socketio.on('frame')
def handle_frame(data):
    """
    Handle incoming frames from the frontend.
    """
    
from flask import Flask, Response, render_template
import cv2
from cvzone.PoseModule import PoseDetector
import math
import numpy as np
import pyttsx3
import threading
import time
import queue
import imageio  # For loading GIFs
from PIL import Image, ImageTk  # For Tkinter compatibility
import tkinter as tk  # For GUI

app = Flask(__name__)

# Initialize Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech

# Initialize video capture and pose detector
cap = cv2.VideoCapture(0)
detector = PoseDetector(detectionCon=0.7, trackCon=0.7)

# Global variables for feedback and threading
feedback_queue = queue.Queue()  # Thread-safe queue for feedback messages
exit_flag = False  # Flag to gracefully exit the program

# Load the GIF
gif_path = "static/k2.gif"  # Replace with your GIF path
gif = imageio.get_reader(gif_path)
gif_frames = [cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) for frame in gif]  # Convert GIF frames to BGR
gif_index = 0  # Current frame index

# Function to speak feedback in a separate thread
def speak_feedback():
    global feedback_queue, exit_flag
    while not exit_flag:
        if not feedback_queue.empty():
            feedback = feedback_queue.get()
            if feedback:
                engine.say(feedback)
                engine.runAndWait()
        time.sleep(0.1)  # Small delay to prevent high CPU usage

# Start the feedback thread
feedback_thread = threading.Thread(target=speak_feedback, daemon=True)
feedback_thread.start()

# Angle Finder Class
class AngleFinder:
    def __init__(self, lmlist, p1, p2, p3, p4, p5, p6, drawPoints):
        self.lmlist = lmlist
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.p5 = p5
        self.p6 = p6
        self.drawPoints = drawPoints

    def angle(self):
        if len(self.lmlist) != 0:
            point1 = self.lmlist[self.p1]
            point2 = self.lmlist[self.p2]
            point3 = self.lmlist[self.p3]
            point4 = self.lmlist[self.p4]
            point5 = self.lmlist[self.p5]
            point6 = self.lmlist[self.p6]

            if len(point1) >= 2 and len(point2) >= 2 and len(point3) >= 2 and len(point4) >= 2 and len(point5) >= 2 and len(
                    point6) >= 2:
                x1, y1 = point1[:2]
                x2, y2 = point2[:2]
                x3, y3 = point3[:2]
                x4, y4 = point4[:2]
                x5, y5 = point5[:2]
                x6, y6 = point6[:2]

                # Calculate angles for left and right arms
                leftHandAngle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
                rightHandAngle = math.degrees(math.atan2(y6 - y5, x6 - x5) - math.atan2(y4 - y5, x4 - x5))

                leftHandAngle = int(np.interp(leftHandAngle, [-170, 180], [100, 0]))
                rightHandAngle = int(np.interp(rightHandAngle, [-50, 20], [100, 0]))

                # Draw circles and lines on selected points
                if self.drawPoints:
                    for (x, y) in [(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x6, y6)]:
                        cv2.circle(img, (x, y), 10, (0, 255, 255), 5)
                        cv2.circle(img, (x, y), 15, (0, 255, 0), 6)

                    cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
                    cv2.line(img, (x2, y2), (x3, y3), (0, 0, 255), 4)
                    cv2.line(img, (x4, y4), (x5, y5), (0, 0, 255), 4)
                    cv2.line(img, (x5, y5), (x6, y6), (0, 0, 255), 4)
                    cv2.line(img, (x1, y1), (x4, y4), (0, 0, 255), 4)

                return [leftHandAngle, rightHandAngle, (x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x6, y6)]
        return None

# Variables for counting and feedback
counter = 0
direction = 0

# Initialize Tkinter GUI
root = tk.Tk()
root.title("AI Trainer")
root.geometry("800x600")

# Create a label to display the video feed
video_label = tk.Label(root)
video_label.pack()

# Function to update the video feed in Tkinter
def update_video_feed():
    global img, gif_index, counter, direction

    ret, img = cap.read()
    if not ret:
        print("Failed to capture image")
        return

    img = cv2.resize(img, (640, 480))

    detector.findPose(img, draw=0)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=0, draw=False)

    angle1 = AngleFinder(lmList, 11, 13, 15, 12, 14, 16, drawPoints=True)
    hands = angle1.angle()
    if hands is not None:
        left, right, p1, p2, p3, p4, p5, p6 = hands[0:]
    else:
        left, right = 45, 45

    # Counting and feedback logic
    if left >= 90 and right >= 90:
        if direction == 0:
            counter += 0.5
            direction = 1
            feedback_queue.put("Good! Keep your shoulders up.")
    if left <= 70 and right <= 70:
        if direction == 1:
            counter += 0.5
            direction = 0
            feedback_queue.put("Lower your shoulders slightly.")

    # Additional Feedback Options
    if hands is not None:
        # 1. Maintain distance between hands
        distance = math.hypot(p3[0] - p6[0], p3[1] - p6[1])
        if distance < 100:
            feedback_queue.put("Maintain more distance between your hands.")
        elif distance > 300:
            feedback_queue.put("Bring your hands closer together.")

        # 2. Raise or lower shoulders
        if left < 70 or right < 70:
            feedback_queue.put(f"Raise your shoulders by {70 - left} degrees.")
        elif left > 90 or right > 90:
            feedback_queue.put(f"Lower your shoulders by {left - 90} degrees.")

        # 3. Move forward or backward (based on hip position)
        if len(lmList) > 23:  # Ensure hip landmarks are detected
            hip_left = lmList[23]  # Left hip landmark
            hip_right = lmList[24]  # Right hip landmark
            hip_center = ((hip_left[0] + hip_right[0]) // 2, (hip_left[1] + hip_right[1]) // 2)

            # Calculate distance from the center of the frame
            frame_center = (img.shape[1] // 2, img.shape[0] // 2)
            hip_offset = hip_center[0] - frame_center[0]

            if hip_offset < -50:
                feedback_queue.put("Move slightly to the right.")
            elif hip_offset > 50:
                feedback_queue.put("Move slightly to the left.")

    # Display feedback on the screen
    if not feedback_queue.empty():
        feedback = feedback_queue.queue[0]  # Peek at the latest feedback
        cv2.putText(img, feedback, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Display hand angles on the screen
    cv2.putText(img, f"Left Hand Angle: {left}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(img, f"Right Hand Angle: {right}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Draw bar-type indicators for left and right hands
    bar_height = 200
    bar_width = 30
    bar_offset = 50

    # Left hand bar
    left_bar_value = np.interp(left, [0, 100], [bar_height, 0])
    cv2.rectangle(img, (bar_offset, bar_height), (bar_offset + bar_width, 0), (0, 255, 0), 2)  # Background
    cv2.rectangle(img, (bar_offset, int(left_bar_value)), (bar_offset + bar_width, bar_height), (0, 255, 0), -1)  # Fill
    cv2.putText(img, "L", (bar_offset, bar_height + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Right hand bar
    right_bar_value = np.interp(right, [0, 100], [bar_height, 0])
    cv2.rectangle(img, (img.shape[1] - bar_offset - bar_width, bar_height), (img.shape[1] - bar_offset, 0), (0, 255, 0), 2)  # Background
    cv2.rectangle(img, (img.shape[1] - bar_offset - bar_width, int(right_bar_value)), (img.shape[1] - bar_offset, bar_height), (0, 255, 0), -1)  # Fill
    cv2.putText(img, "R", (img.shape[1] - bar_offset - bar_width, bar_height + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Display counter and angles
    cv2.rectangle(img, (0, 0), (120, 120), (255, 0, 0), -1)
    cv2.putText(img, str(int(counter)), (1, 70), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.6, (0, 0, 255), 6)

    # Display GIF in the top-right corner
    gif_frame = gif_frames[gif_index]
    gif_frame = cv2.resize(gif_frame, (150, 150))  # Resize GIF to fit
    img[0:150, img.shape[1] - 150: img.shape[1]] = gif_frame  # Overlay GIF on the video feed

    # Update GIF frame index (reduce speed by updating every 2nd iteration)
    gif_index = (gif_index + 1) % len(gif_frames)

    # Convert the OpenCV image to a format compatible with Tkinter
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)

    # Update the video label in Tkinter
    video_label.config(image=img_tk)
    video_label.image = img_tk

    # Schedule the next frame update
    video_label.after(10, update_video_feed)

# Start the video feed update loop
update_video_feed()

# Run the Tkinter main loop
root.mainloop()

# Gracefully exit the program
exit_flag = True
feedback_thread.join()  # Wait for the feedback thread to finish
cap.release()
cv2.destroyAllWindows()
print("Program exited cleanly")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    app.run(debug=True)
    # Decode the base64 image
    frame_data = data.split(',')[1]
    frame_bytes = base64.b64decode(frame_data)
    frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

    # Detect biceps
    processed_frame, biceps_detected = detect_biceps(frame)

    # Encode the processed frame as base64
    _, buffer = cv2.imencode('.jpg', processed_frame)
    processed_frame_data = base64.b64encode(buffer).decode('utf-8')

    # Send the processed frame and detection result back to the frontend
    emit('processed_frame', {
        'frame': f"data:image/jpeg;base64,{processed_frame_data}",
        'biceps_detected': biceps_detected
    })

@app.route('/')
def index():
    return render_template('signup.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)