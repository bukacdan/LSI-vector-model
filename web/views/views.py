from web import app
from flask import render_template, request, redirect, url_for
from web.forms.forms import SearchQueryForm
from web.lsiModel import LSI


lsi = LSI()

@app.route("/", methods=["GET", "POST"])
def index():
    global lsi
    if not lsi.prepared:
        app.logger.info("Preparing LSI.")
        lsi.prepare()
        app.logger.info("LSI prepared!")
    form = SearchQueryForm(formdata=request.form)

    if request.method == "POST":
        lsi.process_query(request.form['query'])
        return redirect(url_for("results"))
    return render_template("homepage.html", form=form)


@app.route("/results")
def results():
    return render_template("results.html", res=lsi.last_query_results, time=lsi.last_query_execution_time)


@app.route("/results/<idx>")
def detail(idx = 0):
    return render_template("detail.html", text=lsi.last_query_results[max(0, int(idx) - 1)])


@app.route("/about")
def about():
    return render_template("about.html")