"""
Clinical Study - Ultrasound Image Analysis
Upload ultrasound images, run AI prediction, and store results.
Uses local storage (SQLite + files) by default, or Supabase (cloud) when configured.
"""
import os
import base64
import csv
import json
from datetime import datetime
from io import StringIO
from pathlib import Path

from flask import Flask, request, render_template, jsonify, Response, send_from_directory
from werkzeug.utils import secure_filename

from model import get_prediction

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}


def get_storage():
    if os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY'):
        from storage_supabase import SupabaseStorage
        return SupabaseStorage()
    from storage_local import LocalStorage
    return LocalStorage()


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
        storage = get_storage()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = file.filename.rsplit('.', 1)[1].lower()
        safe_name = secure_filename(file.filename.rsplit('.', 1)[0])
        filename = f"{safe_name}_{timestamp}.{ext}"

        file_data = file.read()
        filepath, image_url = storage.save_file(file_data, filename)

        payload = base64.b64encode(file_data)
        result = get_prediction(payload)

        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'result': result,
            'image_url': image_url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save', methods=['POST'])
def save_record():
    """Save record to database. Diagnosis is required."""
    data = request.get_json() or {}
    filename = data.get('filename', '').strip()
    filepath = data.get('filepath', '').strip()
    result = data.get('result', '').strip()
    diagnosis = data.get('diagnosis', '').strip()

    if not filename or not result:
        return jsonify({'error': 'Missing filename or result'}), 400
    if not diagnosis:
        return jsonify({'error': 'Actual diagnosis is required'}), 400

    try:
        storage = get_storage()
        if not storage.file_exists(filename) and not filepath:
            return jsonify({'error': 'Image file not found'}), 400

        record_id, image_url = storage.insert_record(filename, filepath or filename, result, diagnosis)

        return jsonify({
            'success': True,
            'id': record_id,
            'number': record_id,
            'filename': filename,
            'result': result,
            'diagnosis': diagnosis,
            'image_url': image_url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve local uploads (only used when not using Supabase)."""
    storage = get_storage()
    if hasattr(storage, 'upload_folder'):
        return send_from_directory(storage.upload_folder, filename)
    return jsonify({'error': 'Not found'}), 404


@app.route('/history')
def history():
    storage = get_storage()
    rows = storage.get_all_records()
    records = [
        {
            'id': r['id'],
            'number': r['id'],
            'filename': r['filename'],
            'result': r['result'],
            'diagnosis': r.get('diagnosis') or '',
            'created_at': r['created_at'],
            'image_url': r.get('image_url') or f"/uploads/{r['filename']}"
        }
        for r in rows
    ]
    return jsonify(records)


@app.route('/export')
def export_data():
    fmt = request.args.get('format', 'csv').lower()
    storage = get_storage()
    rows = storage.get_all_records()
    records = [
        {
            'number': r['id'],
            'filename': r['filename'],
            'ai_prediction': r['result'],
            'actual_diagnosis': r.get('diagnosis') or '',
            'created_at': r['created_at'],
        }
        for r in rows
    ]

    if fmt == 'json':
        return Response(
            json.dumps(records, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=clinical_study_export.json'}
        )

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=['number', 'filename', 'ai_prediction', 'actual_diagnosis', 'created_at'])
    writer.writeheader()
    writer.writerows(records)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=clinical_study_export.csv'}
    )


# Initialize local DB when using local storage
if not (os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY')):
    get_storage()  # Triggers LocalStorage init_db

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f'\n  Ultrasound Analysis running at: http://127.0.0.1:{port}')
    print(f'  Open this URL in Safari or Chrome (not an embedded browser)\n')
    app.run(debug=True, host='127.0.0.1', port=port, threaded=True)
