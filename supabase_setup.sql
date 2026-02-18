-- Run this in Supabase SQL Editor (Dashboard → SQL Editor → New query)

CREATE TABLE IF NOT EXISTS predictions (
  id BIGSERIAL PRIMARY KEY,
  filename TEXT NOT NULL,
  filepath TEXT NOT NULL,
  image_url TEXT,
  result TEXT NOT NULL,
  diagnosis TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Storage policies for uploads bucket (run after creating bucket in UI)
-- Allows uploads and reads - service_role bypasses these but anon may need them
DROP POLICY IF EXISTS "Allow public uploads" ON storage.objects;
CREATE POLICY "Allow public uploads" ON storage.objects FOR INSERT
TO public WITH CHECK (bucket_id = 'uploads');

DROP POLICY IF EXISTS "Allow public read" ON storage.objects;
CREATE POLICY "Allow public read" ON storage.objects FOR SELECT
TO public USING (bucket_id = 'uploads');
