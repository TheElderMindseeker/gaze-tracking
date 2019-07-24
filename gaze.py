"""Gaze trakcing backend"""

import os
import sys
from uuid import uuid4
from base64 import b64decode

import cv2
import numpy as np
from flask import Flask, jsonify, request, url_for, render_template, Blueprint

from model import GazeTrackingModel


N_TRAINING_SAMPLES = os.environ.get('GAZE_N_SAMPLES', 15)
PAGES = ('image1.jpg', 'image2.jpg', 'image3.jpg')


app = Flask(__name__, static_folder='public')  # pylint: disable=invalid-name
static_blueprint = Blueprint('extra_static', __name__, static_folder='public/static', static_url_path='/static')
app.register_blueprint(static_blueprint)
models = dict()  # pylint: disable=invalid-name
frames = dict()  # pylint: disable=invalid-name


def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    decoded_data = b64decode(encoded_data)
    nparr = np.fromstring(decoded_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # pylint: disable=no-member
    print(type(img))
    return img


@app.route('/')
def index():
    """Index page"""
    return app.send_static_file('index.html')


@app.route('/new', methods=['GET'])
def create_model():
    """Creates a model and assigns UUID"""
    return jsonify(model_id=uuid4(), n_samples=N_TRAINING_SAMPLES)


@app.route('/stats')
def get_stats():
    """Gives stats on models"""
    stats = [
        {
            'model_id': model_id,
            'n_frames': len(frame_list)
        }
        for model_id, frame_list in frames.items()
    ]
    return jsonify(stats=stats)


@app.route('/train', methods=['POST'])
def train():
    """Trains the model"""
    if not request.is_json:
        return jsonify(error='Request must be json'), 400

    try:
        frame = data_uri_to_cv2_img(request.json['frame'])
    except:  # pylint: disable=bare-except
        e_type, value, _ = sys.exc_info()
        print(e_type)
        print(value)
        return jsonify(error='Could not decode frame'), 400

    model_id = request.json['model_id']
    coordinates = request.json['coord_x'], request.json['coord_y']
    if model_id not in frames:
        frames[model_id] = list()
    frames[model_id].append((frame, coordinates))

    if len(frames[model_id]) >= N_TRAINING_SAMPLES:
        models[model_id] = GazeTrackingModel(frames[model_id])

    remaining_frames = N_TRAINING_SAMPLES - len(frames[model_id])
    return jsonify(remaining=remaining_frames)


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze the frame and return the results"""
    if not request.is_json:
        return jsonify(error='Request must be json'), 400

    try:
        frame = data_uri_to_cv2_img(request.json['frame'])
    except:  # pylint: disable=bare-except
        return jsonify(error='Could not decode frame'), 400

    model_id = request.json['model_id']
    if model_id not in models:
        return jsonify(error='Model is not trained yet')

    model: GazeTrackingModel = models[model_id]
    model.set_frame(frame)
    frame_info = model.frame_info
    page_index = request.json['index']

    coord_x = frame_info.get('Gaze_x', 0)
    coord_y = frame_info.get('Gaze_y', 0)

    if 'real_x' in request.json and 'real_y' in request.json:
        real_x = request.json['real_x']
        real_y = request.json['real_y']
        real_point = np.array((real_x, real_y), dtype=np.float)
        calc_point = np.array((coord_x, coord_y), dtype=np.float)
        distance = np.linalg.norm(real_point - calc_point)
    else:
        distance = None

    if coord_x >= 900 and coord_y >= 525:
        page_index = min(page_index + 1, len(PAGES) - 1)

    return jsonify(coord_x=coord_x,
                   coord_y=coord_y,
                   distance=distance,
                   image_url=url_for('static', filename=PAGES[page_index]),
                   index=page_index)
