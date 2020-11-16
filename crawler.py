import flask
from flask import request
import argparse
from hct import hct_information as hct

app = flask.Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/test")
def test():
    return hct.testDriver('https://www.google.com/')

@app.route("/hct_com/<deliveryNo>")
def get_hct_delivery(deliveryNo):
    jsonResult = hct.crawler(deliveryNo)
    return jsonResult

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
    #app.run(debug=False, host='0.0.0.0', port=8788)
