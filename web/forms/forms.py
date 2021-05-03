from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class SearchQueryForm(FlaskForm):
    query = StringField(
        'search_query',
        render_kw={'placeholder': 'searched query'},
        validators=[DataRequired()]
    )
    sequential_search = BooleanField(label='search sequentially')
    submit_search = SubmitField('search')
    submit_lsi = SubmitField('initialize LSI')