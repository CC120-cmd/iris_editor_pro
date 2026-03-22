```python
import os
import urllib.request
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
from gfpgan import GFPGANer
from io import BytesIO

app = Flask(__name__)
CORS(app)

print("Starting Face Swap API...")

# =========================
# ✅ MODEL PATHS
# =========================
GFPGAN_MODEL_PATH = "GFPGANv1.4.pth"

# =========================
# ✅ DOWNLOAD GFPGAN MODEL IF MISSING
# =========================
def download_gfpgan():
    if not os.path.exists(GFPGAN_MODEL_PATH):
        print("Downloading GFPGAN model (~340MB)...")
        urllib.request.urlretrieve(
            "https://github.com/TencentARC/GFPGAN/releases/download/v1.4/GFPGANv1.4.pth",
            GFPGAN_MODEL_PATH
        )
        print("GFPGAN model downloaded!")

# =========================
# ✅ LOAD FACE MODELS (CPU SAFE)
# =========================
print("Loading InsightFace...")

face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=-1, det_size=(320, 320))  # CPU mode

print("Loading face swapper...")
swapper = get_model('inswapper_128.onnx', download=True)

# =========================
# ✅ LAZY LOAD GFPGAN (IMPORTANT)
# =========================
restorer = None

def get_restorer():
    global restorer
    if restorer is None:
        download_gfpgan()
        print("Loading GFPGAN...")
        restorer = GFPGANer(
            model_path=GFPGAN_MODEL_PATH,
            upscale=1,
            arch='clean',
            channel_multiplier=2
        )
    return restorer

print("Models initialized successfully!")

# =========================
# ✅ IMAGE RESIZE (PERFORMANCE BOOST)
# =========================
def resize_if_large(img, max_size=640):
    h, w = img.shape[:2]

    if max(h, w) <= max_size:
        return img

    scale = max_size / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)

    return cv2.resize(img, (new_w, new_h))

# =========================
# ✅ ROUTES
# =========================
@app.route('/')
def home():
    return "Face Swap API (Render Ready) is running!"

@app.route('/swap', methods=['POST'])
def swap_faces():
    try:
        if 'source' not in request.files or 'target' not in request.files:
            return jsonify({"error": "Missing images"}), 400

        enhance = request.form.get("enhance") == "true"

        # Read images
        src_file = request.files['source']
        tgt_file = request.files['target']

        src_img = cv2.imdecode(np.frombuffer(src_file.read(), np.uint8), cv2.IMREAD_COLOR)
        tgt_img = cv2.imdecode(np.frombuffer(tgt_file.read(), np.uint8), cv2.IMREAD_COLOR)

        # Resize for speed
        src_img = resize_if_large(src_img)
        tgt_img = resize_if_large(tgt_img)

        # Detect faces
        src_faces = face_app.get(src_img)
        tgt_faces = face_app.get(tgt_img)

        if not src_faces or not tgt_faces:
            return jsonify({"error": "No face detected"}), 400

        src_face = src_faces[0]
        tgt_face = tgt_faces[0]

        print("Swapping faces...")

        # Face swap
        swapped = swapper.get(tgt_img, tgt_face, src_face, paste_back=True)

        # Optional enhancement (lazy loaded)
        if enhance:
            print("Enhancing face...")
            restorer_instance = get_restorer()

            _, _, swapped = restorer_instance.enhance(
                swapped,
                has_aligned=False,
                only_center_face=False,
                paste_back=True
            )

        # Encode result
        _, buffer = cv2.imencode('.jpg', swapped)

        print("Done!")

        return send_file(BytesIO(buffer), mimetype='image/jpeg')

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# =========================
# ✅ LOCAL RUN
# =========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```
