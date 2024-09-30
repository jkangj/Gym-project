from flask import Flask
from views import views, db, bcrypt, login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

app.register_blueprint(views, url_prefix="/views")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the database tables
    app.run(debug=True, port=8000)
