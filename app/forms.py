from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField
from wtforms.validators import InputRequired
from flask_wtf.file import FileRequired, FileAllowed


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class UploadForm(FlaskForm):
    # File field for uploading an image
    file = FileField('Upload Image', validators=[
        FileRequired(),  # File is required
        FileAllowed(['jpg', 'png'], 'Images only!')  # Only allow jpg and png files
    ])