from web import app
from flask import render_template, request, redirect, url_for
from web.forms.forms import SearchQueryForm
from web.lsiModel import LSI


lsi = LSI()


@app.route("/", methods=["GET", "POST"])
def index():
    global lsi
    form = SearchQueryForm(formdata=request.form)

    if request.method == "POST":
        if lsi.prepared:
            query = request.form['query']
            sequential = 'sequential_search' in request.form
            lsi.process_query_seq(query) if sequential else lsi.process_query(query)
            return redirect(url_for("results", seq=sequential))
        else:
            app.logger.info("Preparing LSI.")
            lsi.prepare()
            app.logger.info("LSI prepared!")
    return render_template("homepage.html", form=form, prepared=lsi.prepared)


@app.route("/results")
def results():
    sequential = request.args['seq'] == 'True'
    return render_template("results.html", seq=sequential, res=lsi.last_query_results, time=lsi.last_query_execution_time)


@app.route("/results/<idx>")
def detail(idx = 0):
    return render_template("detail.html", index=idx, text=lsi.last_query_results[max(0, int(idx) - 1)])


@app.route("/about")
def about():
    return render_template("about.html")