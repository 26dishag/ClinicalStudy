# Supabase Setup (5 minutes)

Follow these steps to enable cloud storage so all users see the same data.

---

## 1. Create Supabase project

1. Go to **[supabase.com/dashboard](https://supabase.com/dashboard)**
2. Sign in (or create free account)
3. Click **New Project**
4. Name: `clinical-study` (or anything)
5. Set a database password (save it somewhere)
6. Choose a region
7. Click **Create new project** → wait ~2 min

---

## 2. Run the SQL

1. In your project, click **SQL Editor** (left sidebar)
2. Click **New query**
3. Copy the contents of `supabase_setup.sql` from this folder and paste
4. Click **Run** (or Cmd/Ctrl+Enter)

---

## 3. Create storage bucket

1. Click **Storage** (left sidebar)
2. Click **New bucket**
3. Name: `uploads`
4. Toggle **Public bucket** ON (so images load in the app)
5. Click **Create bucket**

---

## 4. Get credentials

1. Click **Project Settings** (gear icon, bottom left)
2. Click **API** in the menu
3. Copy these two values:
   - **Project URL** (looks like `https://abcdefgh.supabase.co`)
   - **service_role** key (click "Reveal" next to it, then copy)

---

## 5. Add to Railway

1. Open **[railway.app](https://railway.app)** → your project
2. Click your **web** service
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Add:

   | Variable       | Value                    |
   |----------------|--------------------------|
   | `SUPABASE_URL` | (paste Project URL)      |
   | `SUPABASE_KEY` | (paste service_role key) |

6. Railway will redeploy automatically

---

## Done

Your app now uses Supabase. All users will see the same data, and it persists across redeploys.
