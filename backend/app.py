import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
from io import BytesIO

app = Flask(__name__)
CORS(app)

print("Starting Face Swap API (Render mode)...")

# =========================
# LOAD MODELS (CPU SAFE)
# =========================
face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=-1, det_size=(320, 320))

swapper = get_model('inswapper_128.onnx', download=True)

print("Models loaded successfully!")

# =========================
# RESIZE FOR PERFORMANCE
# =========================
def resize_if_large(img, max_size=640):
    h, w = img.shape[:2]

    if max(h, w) <= max_size:
        return img

    scale = max_size / max(h, w)
    return cv2.resize(img, (int(w * scale), int(h * scale)))

# =========================
# ROUTES
# =========================
@app.route('/')
def home():
    return "Face Swap API is running!"

@app.route('/swap', methods=['POST'])
def swap_faces():
    try:
        if 'source' not in request.files or 'target' not in request.files:
            return jsonify({"error": "Missing images"}), 400

        src_file = request.files['source']
        tgt_file = request.files['target']

        src_img = cv2.imdecode(np.frombuffer(src_file.read(), np.uint8), cv2.IMREAD_COLOR)
        tgt_img = cv2.imdecode(np.frombuffer(tgt_file.read(), np.uint8), cv2.IMREAD_COLOR)

        src_img = resize_if_large(src_img)
        tgt_img = resize_if_large(tgt_img)

        src_faces = face_app.get(src_img)
        tgt_faces = face_app.get(tgt_img)

        if not src_faces or not tgt_faces:
            return jsonify({"error": "No face detected"}), 400

        swapped = swapper.get(tgt_img, tgt_faces[0], src_faces[0], paste_back=True)

        _, buffer = cv2.imencode('.jpg', swapped)
        return send_file(BytesIO(buffer), mimetype='image/jpeg')

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)