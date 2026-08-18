import os
import pickle
import numpy as np
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Base path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "Linear_model.pkl")

model = None
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Performance Predictor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px 0;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        .header-title {
            color: #4A0E4E;
            font-weight: 700;
            text-align: center;
            margin-bottom: 25px;
        }
        .btn-predict {
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
            border: none;
            color: white;
            font-weight: bold;
            font-size: 18px;
            border-radius: 30px;
            padding: 12px 30px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4);
        }
        .btn-predict:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 75, 43, 0.6);
            color: white;
        }
        .result-box {
            margin-top: 30px;
            padding: 20px;
            background: #e3f2fd;
            border-left: 5px solid #2196f3;
            border-radius: 10px;
            text-align: center;
        }
    </style>
</head>
<body>

<div class="container d-flex justify-content-center">
    <div class="glass-card">
        <h2 class="header-title">
            <i class="fa-solid fa-graduation-cap"></i> Student Performance Predictor
        </h2>
        
        <form action="/" method="POST">
            <div class="mb-3">
                <label for="hours_studied" class="form-label fw-bold">Hours Studied</label>
                <input type="number" step="0.1" class="form-control" id="hours_studied" name="hours_studied" placeholder="e.g., 7" required value="{{ request.form.get('hours_studied', '') }}">
            </div>

            <div class="mb-3">
                <label for="previous_scores" class="form-label fw-bold">Previous Scores (0-100)</label>
                <input type="number" step="0.1" class="form-control" id="previous_scores" name="previous_scores" placeholder="e.g., 85" required value="{{ request.form.get('previous_scores', '') }}">
            </div>

            <div class="mb-3">
                <label for="extracurricular" class="form-label fw-bold">Extracurricular Activities</label>
                <select class="form-select" id="extracurricular" name="extracurricular" required>
                    <option value="1" {% if request.form.get('extracurricular') == '1' %}selected{% endif %}>Yes</option>
                    <option value="0" {% if request.form.get('extracurricular') == '0' %}selected{% endif %}>No</option>
                </select>
            </div>

            <div class="mb-3">
                <label for="sleep_hours" class="form-label fw-bold">Sleep Hours</label>
                <input type="number" step="0.1" class="form-control" id="sleep_hours" name="sleep_hours" placeholder="e.g., 8" required value="{{ request.form.get('sleep_hours', '') }}">
            </div>

            <div class="mb-3">
                <label for="sample_papers" class="form-label fw-bold">Sample Question Papers Practiced</label>
                <input type="number" class="form-control" id="sample_papers" name="sample_papers" placeholder="e.g., 5" required value="{{ request.form.get('sample_papers', '') }}">
            </div>

            <div class="d-grid mt-4">
                <button type="submit" class="btn btn-predict">
                    <i class="fa-solid fa-wand-magic-sparkles me-2"></i> Predict Score
                </button>
            </div>
        </form>

        {% if prediction_text %}
        <div class="result-box">
            <h4 class="text-primary mb-1">Predicted Performance Index</h4>
            <h2 class="fw-bold text-dark">{{ prediction_text }}</h2>
        </div>
        
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                var count = 200;
                var defaults = { origin: { y: 0.7 } };

                function fire(particleRatio, opts) {
                    confetti(Object.assign({}, defaults, opts, {
                        particleCount: Math.floor(count * particleRatio)
                    }));
                }

                fire(0.25, { spread: 26, startVelocity: 55, colors: ['#ff0000', '#00ff00', '#0000ff'] });
                fire(0.2, { spread: 60, colors: ['#ffff00', '#ff00ff', '#00ffff'] });
                fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8 });
                fire(0.1, { spread: 120, startVelocity: 25, decay: 0.92, colors: ['#ffffff', '#ffbb00'] });
                fire(0.1, { spread: 120, startVelocity: 45 });
            });
        </script>
        {% endif %}
    </div>
</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    prediction_text = None
    if request.method == "POST":
        if model is None:
            prediction_text = "Model pickle file not found!"
        else:
            try:
                hours_studied = float(request.form["hours_studied"])
                previous_scores = float(request.form["previous_scores"])
                extracurricular = float(request.form["extracurricular"])
                sleep_hours = float(request.form["sleep_hours"])
                sample_papers = float(request.form["sample_papers"])

                features = np.array([[hours_studied, previous_scores, extracurricular, sleep_hours, sample_papers]])
                prediction = model.predict(features)[0]
                output = round(float(prediction), 2)

                prediction_text = f"{output} / 100"
            except Exception as e:
                prediction_text = f"Error: {str(e)}"

    return render_template_string(HTML_TEMPLATE, prediction_text=prediction_text)

if __name__ == "__main__":
    app.run(debug=True)
