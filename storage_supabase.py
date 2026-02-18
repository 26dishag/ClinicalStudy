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
        # Bucket created manually in Supabase dashboard - skip to avoid header/options issues
        pass

    def save_file(self, file_data, filename):
        path = f"images/{filename}"
        # Minimal options - avoid bool/header issues; filenames are unique so no upsert needed
        self.client.storage.from_(self.BUCKET).upload(path, file_data)
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
