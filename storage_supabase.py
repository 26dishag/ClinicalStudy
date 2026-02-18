"""Supabase cloud storage backend - PostgreSQL + Storage."""
import os

from supabase import create_client


class SupabaseStorage:
    BUCKET = 'uploads'

    def __init__(self):
        self.client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_KEY']
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.storage.create_bucket(self.BUCKET, options={'public': True})
        except Exception:
            pass  # Bucket likely exists

    def save_file(self, file_data, filename):
        path = f"images/{filename}"
        content_type = 'image/png' if filename.lower().endswith('.png') else 'image/jpeg'
        self.client.storage.from_(self.BUCKET).upload(
            path, file_data,
            file_options={'content-type': content_type, 'upsert': True}
        )
        image_url = self.client.storage.from_(self.BUCKET).get_public_url(path)
        return path, image_url

    def insert_record(self, filename, filepath, result, diagnosis):
        image_url = self.client.storage.from_(self.BUCKET).get_public_url(filepath)
        row = self.client.table('predictions').insert({
            'filename': filename,
            'filepath': filepath,
            'image_url': image_url,
            'result': result,
            'diagnosis': diagnosis,
        }).execute()
        return row.data[0]['id'], image_url

    def get_all_records(self):
        res = self.client.table('predictions').select(
            'id, filename, result, diagnosis, created_at, image_url'
        ).order('id').execute()
        return [
            {
                'id': r['id'],
                'filename': r['filename'],
                'result': r['result'],
                'diagnosis': r.get('diagnosis') or '',
                'created_at': r['created_at'],
                'image_url': r.get('image_url') or ''
            }
            for r in res.data
        ]

    def get_image_url(self, filename):
        return f'/uploads/{filename}'

    def file_exists(self, filename):
        return True
