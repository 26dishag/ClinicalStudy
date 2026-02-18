"""Supabase cloud storage backend - PostgreSQL + Storage.
Uses REST API directly to avoid supabase-py header bool issues.
"""
import os

import requests


class SupabaseStorage:
    BUCKET = 'uploads'

    def __init__(self):
        self.url = os.environ['SUPABASE_URL'].rstrip('/')
        self.key = os.environ['SUPABASE_KEY']
        self._headers = {
            'Authorization': f'Bearer {self.key}',
            'apikey': self.key,
        }

    def save_file(self, file_data, filename):
        path = f"images/{filename}"
        upload_url = f"{self.url}/storage/v1/object/{self.BUCKET}/{path}"
        content_type = 'image/png' if filename.lower().endswith('.png') else 'image/jpeg'
        headers = {**self._headers, 'Content-Type': content_type}
        r = requests.post(upload_url, data=file_data, headers=headers, timeout=30)
        r.raise_for_status()
        image_url = f"{self.url}/storage/v1/object/public/{self.BUCKET}/{path}"
        return path, image_url

    def insert_record(self, filename, filepath, result, diagnosis):
        image_url = f"{self.url}/storage/v1/object/public/{self.BUCKET}/{filepath}"
        headers = {**self._headers, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
        payload = {
            'filename': filename,
            'filepath': filepath,
            'image_url': image_url,
            'result': result,
            'diagnosis': diagnosis,
        }
        r = requests.post(
            f"{self.url}/rest/v1/predictions",
            json=payload,
            headers=headers,
            timeout=30
        )
        r.raise_for_status()
        data = r.json()
        record_id = data[0]['id'] if data else None
        return record_id, image_url

    def get_all_records(self):
        headers = {**self._headers, 'Accept': 'application/json'}
        r = requests.get(
            f"{self.url}/rest/v1/predictions",
            headers=headers,
            params={'order': 'id'},
            timeout=30
        )
        r.raise_for_status()
        rows = r.json()
        return [
            {
                'id': r['id'],
                'filename': r['filename'],
                'result': r['result'],
                'diagnosis': r.get('diagnosis') or '',
                'created_at': r['created_at'],
                'image_url': r.get('image_url') or ''
            }
            for r in rows
        ]

    def get_image_url(self, filename):
        return f'/uploads/{filename}'

    def file_exists(self, filename):
        return True
