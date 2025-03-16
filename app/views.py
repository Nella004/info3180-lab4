import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm, UploadForm

### 
# Routing for your application.
###

# Step 1: Helper function to get a list of uploaded images
def get_uploaded_images():
    image_files = []
    upload_folder = app.config['UPLOAD_FOLDER']  # Update the folder path if needed
    for subdir, dirs, files in os.walk(upload_folder):
        for file in files:
            if file.endswith(('.jpg', '.png')):  # Only include images
                image_files.append(file)
    return image_files


@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    form = UploadForm()

    # Handle file upload on form submission (POST request)
    if form.validate_on_submit():
        # Get the uploaded file from the form
        file = form.file.data

        # Secure the filename and save it to the upload folder
        filename = secure_filename(file.filename)
        upload_folder = app.config['UPLOAD_FOLDER']  # Ensure this is configured
        file.save(os.path.join(upload_folder, filename))

        flash('File successfully uploaded!', 'success')
        return redirect(url_for('home'))  # Redirect to home or another route

    return render_template('upload.html', form=form) 


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():  # Check if the form is valid and submitted
        username = form.username.data
        password = form.password.data

        # Query the UserProfile model to find the user by username
        user = db.session.query(UserProfile).filter_by(username=username).first()

        # If the user exists and the password matches
        if user and check_password_hash(user.password, password):  # Check the hashed password
            # Log the user in
            login_user(user)

            # Flash a success message
            flash('Successfully logged in!', 'success')

            # Redirect the user to the /upload route
            return redirect(url_for("upload"))

        else:
            # If login fails, flash an error message
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template("login.html", form=form)


# Step 2: Create a route to serve images from the upload folder
@app.route('/uploads/<filename>')
def get_image(filename):
    upload_folder = app.config['UPLOAD_FOLDER']  # Ensure this is configured
    return send_from_directory(upload_folder, filename)


# Step 3: Route to list uploaded files
@app.route('/files')
@login_required  # Ensure only logged-in users can access this route
def files():
    image_files = get_uploaded_images()  # Get the list of uploaded images
    return render_template('files.html', image_files=image_files)


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()


### 
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
