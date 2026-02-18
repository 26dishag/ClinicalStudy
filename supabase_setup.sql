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
