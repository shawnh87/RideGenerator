from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class RouteBuildForm(FlaskForm):
    southwest = HiddenField(validators=[DataRequired()])
    northeast = HiddenField(validators=[DataRequired()])
    home = HiddenField(validators=[DataRequired()])
    distance = IntegerField('Desired Distance (miles):',
                            validators=[DataRequired()])
    submit = SubmitField('Generate')
    