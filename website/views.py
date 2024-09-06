from flask import Blueprint, render_template, jsonify, redirect, url_for, Response
import cv2
import mediapipe as mp  # Add this line to import mediapipe
import numpy as np
import time

views = Blueprint(__name__, "views")

def gen_frames():
    cap = cv2.VideoCapture(0)  # 0 is the default camera
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@views.route('/freestyle')
def index():
    return render_template('freestyle.html')

@views.route('/structured')
def structured():
    return render_template('structured.html')

@views.route('/home')
def home():
    return render_template('home.html')


@views.route("/video_feed")
def video_feed():
	return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def draw_button(image, text, position, button_width, text_color=(255, 255, 255)):
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    text_x = position[0] + (button_width - text_size[0]) // 2
    text_y = position[1] + text_size[1]
    cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2, cv2.LINE_AA)
    return (text_x - (button_width - text_size[0]) // 2, text_y - text_size[1]), (text_x + text_size[0] + (button_width - text_size[0]) // 2, text_y)

def gen_bicep_curl_frames():
    cap = cv2.VideoCapture(0)
    mp_pose = mp.solutions.pose
    counter = 0  # Initialize or reset the counter here
    stage = None
    rep_start_time = None
    rep_times = []

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                # Calculate angle
                angle = calculate_angle(shoulder, elbow, wrist)

                # Visualize angle
                cv2.putText(image, str(angle),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Bicep curl counter logic
                if angle > 160:
                    stage = "Down"
                    if rep_start_time is not None:  # If the rep has started
                        rep_end_time = time.time()
                        rep_duration = rep_end_time - rep_start_time
                        if rep_duration >= 1:  # Only count the rep if it took at least 1 second
                            counter += 1
                            rep_times.append(rep_duration)
                        rep_start_time = None  # Reset start time for the next rep

                if angle < 30 and stage == 'Down':
                    stage = "Up"
                    rep_start_time = time.time()  # Start timing the bicep curl

            # Display rep count
            cv2.putText(image, 'REPS', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', image)
            image = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

    cap.release()


@views.route('/bicep_curl_feed')
def bicep_curl_feed():
    return Response(gen_bicep_curl_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route('/bicep_curl')
def bicep_curl():
    return render_template('bicep_curl.html')



def gen_bench_press_frames():
    cap = cv2.VideoCapture(0)
    mp_pose = mp.solutions.pose
    counter = 0
    stage = "Down"
    rep_start_time = None
    rep_times = []

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = calculate_angle(shoulder, elbow, wrist)

                cv2.putText(image, str(angle),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                if angle < 80 and stage != "Up":
                    stage = "Up"
                    if rep_start_time is None:
                        rep_start_time = time.time()

                if angle > 160 and stage == 'Up':
                    stage = "Down"
                    rep_end_time = time.time()
                    rep_duration = rep_end_time - rep_start_time
                    if rep_duration > 1:  # Only count rep if duration is more than 1 second
                        counter += 1
                        rep_times.append(rep_duration)
                    rep_start_time = None

            cv2.putText(image, 'REPS', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', image)
            image = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

    cap.release()

@views.route('/bench_press_feed')
def bench_press_feed():
    return Response(gen_bench_press_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route('/bench_press')
def bench_press():
    return render_template('bench_press.html')

def gen_squat_frames():
    cap = cv2.VideoCapture(0)
    mp_pose = mp.solutions.pose
    counter = 0
    stage = "Up"
    rep_start_time = None
    rep_times = []

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates for squat detection
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                # Calculate angle
                angle = calculate_angle(hip, knee, ankle)

                # Visualize angle
                cv2.putText(image, str(angle),
                            tuple(np.multiply(knee, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Squat counter logic
                if angle > 160:
                    stage = "Up"
                    if rep_start_time is not None:  # If the rep has started
                        rep_end_time = time.time()
                        rep_duration = rep_end_time - rep_start_time
                        if rep_duration >= 1:  # Only count the rep if it took at least 1 second
                            counter += 1
                            rep_times.append(rep_duration)
                        rep_start_time = None  # Reset start time for the next rep

                if angle < 90 and stage == 'Up':
                    stage = "Down"
                    rep_start_time = time.time()  # Start timing the squat

            # Display squat count
            cv2.putText(image, 'REPS', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', image)
            image = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

    cap.release()

@views.route('/squat_feed')
def squat_feed():
    return Response(gen_squat_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route('/squat')
def squat():
    return render_template('squat.html')

def gen_pull_down_frames():
    cap = cv2.VideoCapture(0)
    mp_pose = mp.solutions.pose
    counter = 0
    stage = "Up"
    rep_start_time = None
    rep_times = []

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                # Calculate angle
                angle = calculate_angle(shoulder, elbow, wrist)

                # Visualize angle
                cv2.putText(image, str(angle),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Pull-down rep counter logic
                if angle > 160:
                    stage = "Up"
                    if rep_start_time is not None:  # If the rep has started
                        rep_end_time = time.time()
                        rep_duration = rep_end_time - rep_start_time
                        if rep_duration >= 1:  # Only count the rep if it took at least 1 second
                            counter += 1
                            rep_times.append(rep_duration)
                        rep_start_time = None  # Reset start time for the next rep

                if angle < 45 and stage == 'Up':
                    stage = "Down"
                    rep_start_time = time.time()  # Start timing the pull-down

            # Display rep count
            cv2.putText(image, 'REPS', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', image)
            image = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

    cap.release()

@views.route('/pull_down_feed')
def pull_down_feed():
    return Response(gen_pull_down_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route('/pull_down')
def pull_down():
    return render_template('pull_down.html')

def gen_shoulder_press_frames():
    cap = cv2.VideoCapture(0)
    mp_pose = mp.solutions.pose
    counter = 0
    stage = "Down"
    rep_start_time = None
    rep_times = []

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                # Calculate angle
                angle = calculate_angle(shoulder, elbow, wrist)

                # Visualize angle
                cv2.putText(image, str(angle),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Shoulder press counter logic
                if angle > 160:
                    stage = "Down"
                    if rep_start_time is not None:  # If the rep has started
                        rep_end_time = time.time()
                        rep_duration = rep_end_time - rep_start_time
                        if rep_duration >= 1:  # Only count the rep if it took at least 1 second
                            counter += 1
                            rep_times.append(rep_duration)
                        rep_start_time = None  # Reset start time for the next rep

                if angle < 45 and stage == 'Down':
                    stage = "Up"
                    rep_start_time = time.time()  # Start timing the shoulder press

            # Display rep count
            cv2.putText(image, 'REPS', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', image)
            image = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

    cap.release()

@views.route('/shoulder_press_feed')
def shoulder_press_feed():
    return Response(gen_shoulder_press_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route('/shoulder_press')
def shoulder_press():
    return render_template('shoulder_press.html')


""" Extra stuff

@views.route("/json")
def get_json():
	return jsonify({'name':'john','coolness':100})

@views.route("/data")
def get_data():
	data = request.json
	return jsonify(data)

@views.route("/go-to-home")
def go_to_home():
	return redirct(url_for("views.home"))
"""


