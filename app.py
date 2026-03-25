import os
os.environ["OMP_NUM_THREADS"] = "1"

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model

app = Flask(__name__)
CORS(app)

print("Starting Face Swap API...")

# =========================
# GLOBAL MODELS (LAZY LOAD)
# =========================
face_app = None
swapper = None

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
# HOME ROUTE
# =========================
@app.route('/')
def home():
    return "Face Swap API is running!"

# =========================
# SWAP ROUTE
# =========================
@app.route('/swap', methods=['POST'])
def swap_faces():
    global face_app, swapper

    try:
        # =========================
        # LOAD MODELS ONCE
        # =========================
        if face_app is None:
            print("Loading face model...")
            face_app = FaceAnalysis(name='buffalo_l')
            face_app.prepare(ctx_id=-1, det_size=(320, 320))  # balanced speed/accuracy

        if swapper is None:
            print("Loading swapper model...")
            swapper = get_model('inswapper_128.onnx', download=True)

        # =========================
        # VALIDATE INPUT
        # =========================
        if 'source' not in request.files or 'target' not in request.files:
            return jsonify({"error": "Missing images"}), 400

        src_file = request.files['source']
        tgt_file = request.files['target']

        # =========================
        # READ IMAGES
        # =========================
        src_img = cv2.imdecode(
            np.frombuffer(src_file.read(), np.uint8),
            cv2.IMREAD_COLOR
        )

        tgt_img = cv2.imdecode(
            np.frombuffer(tgt_file.read(), np.uint8),
            cv2.IMREAD_COLOR
        )

        if src_img is None or tgt_img is None:
            return jsonify({"error": "Invalid image format"}), 400

        # =========================
        # RESIZE
        # =========================
        src_img = resize_if_large(src_img)
        tgt_img = resize_if_large(tgt_img)

        # =========================
        # DETECT FACES
        # =========================
        src_faces = face_app.get(src_img)
        tgt_faces = face_app.get(tgt_img)

        if not src_faces:
            return jsonify({"error": "No face in source image"}), 400
        if not tgt_faces:
            return jsonify({"error": "No face in target image"}), 400

        # =========================
        # FACE SWAP
        # =========================
        result = swapper.get(
            tgt_img,
            tgt_faces[0],
            src_faces[0],
            paste_back=True
        )

        if result is None:
            return jsonify({"error": "Face swap failed"}), 500

        # =========================
        # FIX IMAGE FORMAT
        # =========================
        result = np.clip(result, 0, 255).astype(np.uint8)

        # =========================
        # ENCODE IMAGE
        # =========================
        success, buffer = cv2.imencode('.jpg', result)

        if not success:
            return jsonify({"error": "Image encoding failed"}), 500

        # =========================
        # RETURN IMAGE (FIXED)
        # =========================
        return Response(
            buffer.tobytes(),
            mimetype='image/jpeg',
            headers={
                "Content-Disposition": "inline; filename=swap.jpg"
            }
        )

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)