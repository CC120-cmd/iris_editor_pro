import os

# =========================
# 🔥 LIMIT THREADS (CRITICAL FOR RENDER FREE)
# =========================
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

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
# 🔥 LOAD LIGHTWEIGHT MODEL (FREE PLAN SAFE)
# =========================
print("Loading models at startup...")

face_app = FaceAnalysis(name='buffalo_s')  # 🔥 lightweight model
face_app.prepare(ctx_id=-1, det_size=(160, 160))  # 🔥 reduced size

swapper = get_model('inswapper_128.onnx', download=True)

print("Models loaded successfully")

# =========================
# RESIZE
# =========================
def resize_if_large(img, max_size=640):
    h, w = img.shape[:2]
    if max(h, w) <= max_size:
        return img
    scale = max_size / max(h, w)
    return cv2.resize(img, (int(w * scale), int(h * scale)))

# =========================
# HOME
# =========================
@app.route('/')
def home():
    return "Face Swap API is running!"

# =========================
# SWAP
# =========================
@app.route('/swap', methods=['POST'])
def swap_faces():
    try:
        # =========================
        # VALIDATE
        # =========================
        if 'source' not in request.files or 'target' not in request.files:
            return jsonify({"error": "Missing images"}), 400

        # =========================
        # READ IMAGES
        # =========================
        src_img = cv2.imdecode(
            np.frombuffer(request.files['source'].read(), np.uint8),
            cv2.IMREAD_COLOR
        )

        tgt_img = cv2.imdecode(
            np.frombuffer(request.files['target'].read(), np.uint8),
            cv2.IMREAD_COLOR
        )

        if src_img is None or tgt_img is None:
            return jsonify({"error": "Invalid image"}), 400

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
            return jsonify({"error": "No face in source"}), 400
        if not tgt_faces:
            return jsonify({"error": "No face in target"}), 400

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
            return jsonify({"error": "Swap failed"}), 500

        # =========================
        # 🔥 ROBUST IMAGE FIX
        # =========================
        result = np.nan_to_num(result)

        if result.dtype in [np.float32, np.float64]:
            if result.max() <= 1.0:
                result = result * 255
            result = np.clip(result, 0, 255)

        result = result.astype(np.uint8)

        if len(result.shape) == 2:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

        if len(result.shape) == 3 and result.shape[2] == 4:
            result = cv2.cvtColor(result, cv2.COLOR_BGRA2BGR)

        result = np.ascontiguousarray(result)

        # =========================
        # ENCODE (JPG FIRST)
        # =========================
        success, buffer = cv2.imencode(
            '.jpg',
            result,
            [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        )

        if success and buffer is not None:
            data = buffer.tobytes()
            print("JPG size:", len(data))

            if len(data) > 5000:
                return Response(
                    data,
                    mimetype='image/jpeg',
                    headers={
                        "Content-Disposition": "inline; filename=swap.jpg",
                        "Content-Length": str(len(data))
                    }
                )

        # =========================
        # 🔥 FALLBACK TO PNG
        # =========================
        print("Falling back to PNG...")

        success, buffer = cv2.imencode('.png', result)

        if not success or buffer is None:
            return jsonify({"error": "Encoding failed"}), 500

        data = buffer.tobytes()
        print("PNG size:", len(data))

        return Response(
            data,
            mimetype='image/png',
            headers={
                "Content-Disposition": "inline; filename=swap.png",
                "Content-Length": str(len(data))
            }
        )

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)