from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kyc.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

# Define database model for User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    contact_number = db.Column(db.String(15))
    address = db.Column(db.String(200))
    pan_card_number = db.Column(db.String(20))
    aadhar_card_number = db.Column(db.String(20))
    profession = db.Column(db.String(100))
    pan_card_filename = db.Column(db.String(255))
    aadhar_card_filename = db.Column(db.String(255))

# Flask-Login callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Route for dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Route for document upload
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        name = request.form['name']
        contact_number = request.form['contact_number']
        address = request.form['address']
        pan_card_number = request.form['pan_card_number']
        aadhar_card_number = request.form['aadhar_card_number']
        profession = request.form['profession']
        user = current_user
        user.name = name
        user.contact_number = contact_number
        user.address = address
        user.pan_card_number = pan_card_number
        user.aadhar_card_number = aadhar_card_number
        user.profession = profession
        db.session.commit()

        pan_card_file = request.files['pan_card_file']
        if pan_card_file:
            pan_card_filename = secure_filename(pan_card_file.filename)
            pan_card_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pan_card_filename))
            user.pan_card_filename = pan_card_filename

        aadhar_card_file = request.files['aadhar_card_file']
        if aadhar_card_file:
            aadhar_card_filename = secure_filename(aadhar_card_file.filename)
            aadhar_card_file.save(os.path.join(app.config['UPLOAD_FOLDER'], aadhar_card_filename))
            user.aadhar_card_filename = aadhar_card_filename

        db.session.commit()

        flash('Files uploaded successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('upload.html')

# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
