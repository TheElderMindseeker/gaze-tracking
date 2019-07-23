"""Gaze trakcing backend"""

from flask import Flask


app = Flask(__name__)  # pylint: disable=invalid-name


@app.route('/', methods=['POST'])
def gaze():
    """Gets all the job done"""
