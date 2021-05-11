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


@app.route("/results/<idx_document_url>")
def detail(idx_document_url):
    global lsi

    if not lsi.prepared:
        return redirect(url_for("index"))
    document = lsi.last_document_results[max(0, int(request.args["idx_loop"]) - 1)] if request.args["similar"] == "True" else lsi.last_query_results[max(0, int(request.args["idx_loop"]) - 1)]
    lsi.process_document(int(request.args["idx_document"]))
    return render_template("detail.html", document=document, similar_documents=lsi.last_document_results)


@app.route("/about")
def about():
    return render_template("about.html")