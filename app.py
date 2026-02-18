"""
Clinical Study - Ultrasound Image Analysis
Upload ultrasound images, run AI prediction, and store results.
"""
import os
import base64
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request, render_template, jsonify, Response
from werkzeug.utils import secure_filename

from model import get_prediction

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
# Use DATA_DIR for persistent storage on Railway/Render (set in env, or default to app dir)
_data_dir = Path(os.environ.get('DATA_DIR', Path(__file__).parent))
app.config['UPLOAD_FOLDER'] = _data_dir / 'uploads'
app.config['DATABASE'] = _data_dir / 'clinical_study.db'

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)


def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            result TEXT NOT NULL,
            diagnosis TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Add diagnosis column if migrating from old schema
    try:
        conn.execute('ALTER TABLE predictions ADD COLUMN diagnosis TEXT DEFAULT \'\'')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running'})


@app.route('/upload', methods=['POST'])
def upload_image():
    """Analyze image and return prediction. Does not save until diagnosis is provided."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, bmp, webp'}), 400

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = file.filename.rsplit('.', 1)[1].lower()
        safe_name = secure_filename(file.filename.rsplit('.', 1)[0])
        filename = f"{safe_name}_{timestamp}.{ext}"
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(filepath)

        with open(filepath, 'rb') as img:
            payload = base64.b64encode(img.read())
        result = get_prediction(payload)

        return jsonify({
            'success': True,
            'filename': filename,
            'result': result,
            'image_url': f'/uploads/{filename}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save', methods=['POST'])
def save_record():
    """Save record to database. Diagnosis is required."""
    data = request.get_json() or {}
    filename = data.get('filename', '').strip()
    result = data.get('result', '').strip()
    diagnosis = data.get('diagnosis', '').strip()

    if not filename or not result:
        return jsonify({'error': 'Missing filename or result'}), 400
    if not diagnosis:
        return jsonify({'error': 'Actual diagnosis is required'}), 400

    filepath = Path(app.config['UPLOAD_FOLDER']) / filename
    if not filepath.exists():
        return jsonify({'error': 'Image file not found'}), 400

    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO predictions (filename, filepath, result, diagnosis) VALUES (?, ?, ?, ?)',
            (filename, str(filepath), result, diagnosis)
        )
        conn.commit()
        record_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()

        return jsonify({
            'success': True,
            'id': record_id,
            'number': record_id,
            'filename': filename,
            'result': result,
            'diagnosis': diagnosis,
            'image_url': f'/uploads/{filename}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/uploads/<filename>')
def serve_upload(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/history')
def history():
    conn = get_db()
    rows = conn.execute(
        'SELECT id, filename, result, diagnosis, created_at FROM predictions ORDER BY id ASC'
    ).fetchall()
    conn.close()

    records = [
        {
            'id': r['id'],
            'number': r['id'],
            'filename': r['filename'],
            'result': r['result'],
            'diagnosis': r['diagnosis'] or '',
            'created_at': r['created_at'],
            'image_url': f"/uploads/{r['filename']}"
        }
        for r in rows
    ]
    return jsonify(records)


@app.route('/export')
def export_data():
    fmt = request.args.get('format', 'csv').lower()
    conn = get_db()
    rows = conn.execute(
        'SELECT id, filename, result, diagnosis, created_at FROM predictions ORDER BY id ASC'
    ).fetchall()
    conn.close()

    records = [
        {
            'number': r['id'],
            'filename': r['filename'],
            'ai_prediction': r['result'],
            'actual_diagnosis': r['diagnosis'] or '',
            'created_at': r['created_at'],
        }
        for r in rows
    ]

    if fmt == 'json':
        import json
        return Response(
            json.dumps(records, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=clinical_study_export.json'}
        )

    # CSV
    import csv
    from io import StringIO
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=['number', 'filename', 'ai_prediction', 'actual_diagnosis', 'created_at'])
    writer.writeheader()
    writer.writerows(records)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=clinical_study_export.csv'}
    )


# Initialize DB when app loads (for gunicorn)
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f'\n  Ultrasound Analysis running at: http://127.0.0.1:{port}')
    print(f'  Open this URL in Safari or Chrome (not an embedded browser)\n')
    app.run(debug=True, host='127.0.0.1', port=port, threaded=True)
