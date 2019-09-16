import flask_wtf
import wtforms

class LoginForm(flask_wtf.FlaskForm):
    submit = wtforms.SubmitField('Record Point')