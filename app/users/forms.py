from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError

from wtforms import HiddenField, SubmitField

from wtforms import PasswordField
from wtforms.validators import EqualTo, Optional

from flask_wtf.file import FileField, FileAllowed, FileRequired

class ProfilePicForm(FlaskForm):
    picture = FileField('Upload Profile Picture', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Upload')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])

    password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[Optional(), EqualTo('password', message='Passwords must match')])

    submit = SubmitField('Save Changes')



class ProfileViewRequestForm(FlaskForm):
    profile_owner_id = HiddenField('Profile Owner ID')  # set this in your route/template
    submit = SubmitField('Request Access')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=140)])
    body = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=140)])
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Update Post')
