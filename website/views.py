
from flask import Blueprint, render_template, jsonify, redirect, url_for, Response, request, session
import cv2
import mediapipe as mp
from datetime import datetime
import time
from flask import flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager, 
    UserMixin, 
    login_user, 
    current_user, 
    logout_user, 
    login_required, 
    AnonymousUserMixin
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import numpy as np


views = Blueprint(__name__, "views")


db = SQLAlchemy()  
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'views.login'


# User model 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    exercise_data = db.relationship('ExerciseData', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"



# ExerciseData model 
class ExerciseData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(100), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_performed = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ExerciseData('{self.exercise}', {self.reps}, {self.weight} lbs, '{self.date_performed}')"



@views.route('/save_bicep_curl_set', methods=['POST'])
@login_required
def save_bicep_curl_set():
    data = request.get_json()  # Get data from the POST request
    exercise = data.get('exercise')
    reps = data.get('reps')
    weight = data.get('weight')

    if exercise and reps and weight:
        # Create a new ExerciseData entry
        new_data = ExerciseData(
            exercise=exercise,
            reps=reps,
            weight=weight,
            user_id=current_user.id  # Associate the data with the current user
        )
        db.session.add(new_data)
        db.session.commit()
        reps = 0
        return jsonify({"message": "Exercise data saved successfully!"}), 200

    return jsonify({"message": "Failed to save data"}), 400

@views.route('/save_bench_press_set', methods=['POST'])
@login_required
def save_bench_press_set():
    data = request.get_json()  # Get data from the POST request
    exercise = "Bench Press"
    reps = data.get('reps')
    weight = data.get('weight')

    if reps and weight:
        # Create a new ExerciseData entry
        new_data = ExerciseData(
            exercise=exercise,
            reps=reps,
            weight=weight,
            user_id=current_user.id  # Associate the data with the current user
        )
        db.session.add(new_data)
        db.session.commit()

        return jsonify({"message": "Bench Press data saved successfully!"}), 200

    return jsonify({"message": "Failed to save data"}), 400

@views.route('/save_squat_set', methods=['POST'])
@login_required
def save_squat_set():
    data = request.get_json()  # Get data from the POST request
    exercise = "Squat"
    reps = data.get('reps')
    weight = data.get('weight')

    if reps and weight:
        # Create a new ExerciseData entry
        new_data = ExerciseData(
            exercise=exercise,
            reps=reps,
            weight=weight,
            user_id=current_user.id  # Associate the data with the current user
        )
        db.session.add(new_data)
        db.session.commit()

        return jsonify({"message": "Squat data saved successfully!"}), 200

    return jsonify({"message": "Failed to save data"}), 400



@views.route('/save_pull_down_set', methods=['POST'])
@login_required
def save_pull_down_set():
    print("Received POST request to save pull-down set")  
    data = request.get_json()  
    exercise = "Pull Down"
    reps = data.get('reps')
    weight = data.get('weight')
    print(f"Received reps: {reps}, weight: {weight}") 

    if reps and weight:
        # Create a new ExerciseData entry
        new_data = ExerciseData(
            exercise=exercise,
            reps=reps,
            weight=weight,
            user_id=current_user.id  # Associate the data with the current user
        )
        db.session.add(new_data)
        db.session.commit()
        print("Data saved successfully!")  # Confirm saving was successful
        return jsonify({"message": "Pull Down data saved successfully!"}), 200

    print("Failed to save data due to missing reps or weight")  # Log error case
    return jsonify({"message": "Failed to save data"}), 400


@views.route('/save_shoulder_press_set', methods=['POST'])
@login_required
def save_shoulder_press_set():
    data = request.get_json()  # Get data from the POST request
    exercise = "Shoulder Press"
    reps = data.get('reps')
    weight = data.get('weight')

    if reps and weight:
        # Create a new ExerciseData entry
        new_data = ExerciseData(
            exercise=exercise,
            reps=reps,
            weight=weight,
            user_id=current_user.id  
        )
        db.session.add(new_data)
        db.session.commit()

        return jsonify({"message": "Shoulder Press data saved successfully!"}), 200

    return jsonify({"message": "Failed to save data"}), 400



@views.route('/my_exercises')
@login_required
def my_exercises():
    user_exercises = ExerciseData.query.filter_by(user_id=current_user.id).all()
    return render_template('my_exercises.html', exercises=user_exercises)

@views.route('/reset_reps', methods=['POST'])
def reset_reps():
    global reps
    reps = 0
    return 'Reps reset', 200

@views.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
@login_required
def delete_exercise(exercise_id):
    exercise = ExerciseData.query.get_or_404(exercise_id)
    if exercise.user_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403
    
    db.session.delete(exercise)
    db.session.commit()
    return redirect(url_for('views.my_exercises'))


# Define the user_loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered.')

# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

@views.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # Redirect authenticated users to the home page
        return redirect(url_for('views.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password and create the user
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('views.login'))  # Redirect to login after registration
    return render_template('register.html', form=form)



@views.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect authenticated users to the home page
        return redirect(url_for('views.home'))

    form = LoginForm()
    if form.validate_on_submit():
        # Fetch the user from the database
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Log the user in
            login_user(user, remember=form.remember.data)
            
            # Redirect to next page if available, otherwise to home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('views.home'))
        else:
            # Show an error message if login failed
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)


# Logout Route
@views.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('views.home'))

# Home Page (Protected)
@views.route("/home")
@login_required
def home():
    return render_template('home.html')

@views.route('/get_reps')
def get_reps():
    global reps
    return jsonify({'reps': reps})

# Function to generate video frames for general video feed
def gen_frames():
    cap = cv2.VideoCapture(0)  
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



# Route to display freestyle page
@views.route('/freestyle')
def index():
    return render_template('freestyle.html')

# Route to display structured page
@views.route('/structured')
def structured():
    return render_template('structured.html')



# Route to display general video feed
@views.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Function to calculate the angle between three points (for pose tracking)
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# Function to draw a button on an image 
def draw_button(image, text, position, button_width, text_color=(255, 255, 255)):
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    text_x = position[0] + (button_width - text_size[0]) // 2
    text_y = position[1] + text_size[1]
    cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2, cv2.LINE_AA)
    return (text_x - (button_width - text_size[0]) // 2, text_y - text_size[1]), (text_x + text_size[0] + (button_width - text_size[0]) // 2, text_y)

# Initialize reps globally
reps = 0
stage = None

# Function to generate real-time bicep curl frames with pose tracking
def gen_bicep_curl_frames():
    global reps  # Use the global reps variable
    cap = cv2.VideoCapture(0)
    mp_pose = mp.solutions.pose
    counter = 0  # Local counter for reps within this function
    stage = None
    rep_start_time = None  # Variable to track the start time of a rep

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)  # Flip for a mirrored effect
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates for left side
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                
                angle = calculate_angle(shoulder, elbow, wrist)

              
                if angle > 160:  # When the arm is fully extended
                    stage = "down"  # Reset stage to down for the next rep
                    if rep_start_time is not None:
                        rep_duration = time.time() - rep_start_time
                        if rep_duration >= 1:  # Only count the rep if it took at least 1 second
                            counter += 1
                            reps = counter  # Update global reps count
                            rep_start_time = None  # Reset the timer after counting the rep

                if angle < 30 and stage == "down":  # When the arm is fully contracted and ready for another rep
                    stage = "up"
                    rep_start_time = time.time()  # Start timing the rep

            # Display reps count on the video
            cv2.putText(image, 'REPS', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter), (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    print(counter)
    counter = 0

    cap.release()



# Route to display bicep curl feed
@views.route('/bicep_curl_feed')
def bicep_curl_feed():
    return Response(gen_bicep_curl_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to display the bicep curl page
@views.route('/bicep_curl')
def bicep_curl():
    exercise_type = "Bicep Curl"  # Set exercise type
    return render_template('bicep_curl.html', exercise_type=exercise_type)  # Pass it to the HTML



def gen_bench_press_frames():
    global reps  # Use the global reps variable
    cap = cv2.VideoCapture(0)

    mp_pose = mp.solutions.pose
    counter = -1  # Local counter for reps within this function
    stage = "Down"
    rep_start_time = None  # Variable to track the start time of a rep

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

                # Get coordinates for left side
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                # Calculate angle
                angle = calculate_angle(shoulder, elbow, wrist)

                # Bench press logic with 1-second rule
                if angle > 160 and stage == "Up":  # Top of the press
                    rep_end_time = time.time()
                    rep_duration = rep_end_time - rep_start_time
                    if rep_duration >= 1:  # Count only if it took more than 1 second
                        counter += 1
                        reps = counter  # Update global reps count
                    stage = "Down"  # Reset stage to Down for the next rep
                    rep_start_time = None  # Reset the timer for the next rep

                if angle < 80 and stage != "Up":  # Bottom of the press
                    stage = "Up"
                    rep_start_time = time.time()  # Start timing the rep

            # Conditionally display the rep count (show 0 if counter is -1)
            display_counter = counter if counter >= 0 else 0

            # Display the rep count on the video
            cv2.putText(image, 'REPS', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(image, str(display_counter), (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


@views.route('/bench_press_feed')
def bench_press_feed():
    return Response(gen_bench_press_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route('/bench_press')
def bench_press():
    return render_template('bench_press.html')

def gen_squat_frames():
    global reps  # Use the global reps variable if tracking globally
    cap = cv2.VideoCapture(0)
    mp_pose = mp.solutions.pose
    counter = 0
    stage = "Up"
    rep_start_time = None  # Track the start time of a rep

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

                # Calculate angle for squat (hip, knee, ankle)
                angle = calculate_angle(hip, knee, ankle)

                
                # Squat logic with 2-second rule
                if angle > 160 and stage == "Down":  # Standing up (top of the squat)
                    rep_end_time = time.time()
                    if rep_start_time is not None:
                        rep_duration = rep_end_time - rep_start_time
                        if rep_duration >= 2:  # Only count the rep if it took at least 1 second
                            counter += 1
                            reps = counter  # Update global reps count if needed
                    stage = "Up"  # Reset stage to Up for the next rep
                    rep_start_time = None  # Reset start time for next rep

                if angle < 90 and stage == "Up":  # Squatting down (bottom of the squat)
                    stage = "Down"
                    rep_start_time = time.time()  # Start timing the squat

            # Display squat count
            cv2.putText(image, 'REPS', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter), (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 2, cv2.LINE_AA)

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
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 2, cv2.LINE_AA)

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
