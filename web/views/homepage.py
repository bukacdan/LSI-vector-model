from flask import render_template
from web import app
from web.forms import SearchQueryForm


@app.route("/")
def index():
    form = SearchQueryForm()
    return render_template("homepage.html", form=form)
