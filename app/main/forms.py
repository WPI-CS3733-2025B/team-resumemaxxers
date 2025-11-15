from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class ApplyPositionForm(FlaskForm):
    statement = TextAreaField("Short statement",
        validators=[
            DataRequired(message="Please enter your short statement."),
            Length(min=10, max=1500, message="Statement must be between 10 and 1500 characters.")
        ]
    )

    reference_email = StringField("Reference Email (if required)", validators=[Optional(), Email(message="Invalid email format.")])

    submit = SubmitField("Apply")