"""Local storage backend - SQLite + filesystem."""
import os
import sqlite3
from pathlib import Path


class LocalStorage:
    def __init__(self):
        self.data_dir = Path(os.environ.get('DATA_DIR', Path(__file__).parent))
        self.upload_folder = self.data_dir / 'uploads'
        self.db_path = self.data_dir / 'clinical_study.db'
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
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
        try:
            conn.execute('ALTER TABLE predictions ADD COLUMN diagnosis TEXT DEFAULT ""')
            conn.commit()
        except sqlite3.OperationalError:
            pass
        conn.close()

    def save_file(self, file_data, filename):
        filepath = self.upload_folder / filename
        filepath.write_bytes(file_data)
        return str(filepath), f'/uploads/{filename}'

    def insert_record(self, filename, filepath, result, diagnosis):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute(
            'INSERT INTO predictions (filename, filepath, result, diagnosis) VALUES (?, ?, ?, ?)',
            (filename, filepath, result, diagnosis)
        )
        conn.commit()
        row_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        return row_id, f'/uploads/{filename}'

    def get_all_records(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            'SELECT id, filename, result, diagnosis, created_at FROM predictions ORDER BY id ASC'
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_image_url(self, filename):
        return f'/uploads/{filename}'

    def file_exists(self, filename):
        return (self.upload_folder / filename).exists()
