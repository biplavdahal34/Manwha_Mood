from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, NumberRange, EqualTo, ValidationError, Length, Email
from manhwaapp.models import User


class RegisterForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Length(min=6, max=50),Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = StringField("Confirm Password", validators=[DataRequired(), Length(min=8),EqualTo('password')])
    submit = SubmitField("Create Account")

    def validate_username(self, field):
        existing_username = User.query.filter_by(username= field.data).first()
        if existing_username:
            raise ValidationError("Username Already Exists. Please Try Another One!")

    def validate_email(self, field):
        exiting_email = User.query.filter_by(email = field.data).first()
        if exiting_email:
            raise ValidationError("Email Already Exists, Please Enter Another One!")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(),Length(min=0, max=20)])
    password = PasswordField("Password",validators= [DataRequired(),Length(min=0)])
    submit = SubmitField("Log In")

class SearchForm(FlaskForm):
    search_name = StringField("Search", validators=[DataRequired()])

class OTPForm(FlaskForm):
    otp = StringField("OTP", validators=[DataRequired()])
    submit = SubmitField('Verify')

