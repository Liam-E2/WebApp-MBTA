from mbta_helper import find_stop_near

"""
Simple "Hello, World" application using Flask
"""

from flask import Flask, render_template, request, redirect
from werkzeug.exceptions import InternalServerError



app = Flask(__name__)
    

@app.route('/')
def hello_world():
    return render_template('main.html')


@app.route('/post/<place_name>')
def show_post(place_name):
    # show the post with the given id, the id is an integer
    pn = find_stop_near(place_name)
    
    return render_template('response.html', place_name=pn)


@app.route("/find_stop", methods=['POST'])
def find_stop():
    """Triggered by HTML form, returns template for response"""
    # Extract form data
    loc = request.form['location']
    station_type = request.form['type']

    # Default no station type
    if station_type[0] == "S":
        station_type = None
    
    # Find Stop & Populate Template
    result = find_stop_near(loc, station_type=station_type)
    
    return render_template("response.html", place_name=result[0], wheelchair_accessible=result[1])


@app.errorhandler(InternalServerError)
def handle_500(e):
    """From flask docs for generic 500 error handler; redirects internal server errors to a default error page"""
    original = getattr(e, "original_exception", None)

    if original is None:
        # direct 500 error, such as abort(500)
        return render_template("error.html"), 500

    # wrapped unhandled error
    return render_template("error.html"), 500
