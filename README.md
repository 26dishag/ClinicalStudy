# Clinical Study - Ultrasound Image Analysis

A web application for uploading ultrasound images, running them through an AI model for analysis, and storing both the images and results.

## Features

- **Upload UI**: Drag-and-drop or click to upload ultrasound images (PNG, JPG, GIF, BMP, WebP)
- **AI Analysis**: Images are sent to the AI model API for prediction
- **Result Display**: Shows the uploaded image alongside the predicted label
- **Storage**: Images saved to `uploads/` folder; metadata and results stored in SQLite database (`clinical_study.db`)
- **History**: View all previous analyses with thumbnails and results

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open **http://127.0.0.1:5001** in Safari or Chrome (not an embedded/in-app browser).

   Or run `./run.sh` from the project folder.

## Deploy to Railway

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step instructions to host this app on Railway or Render.

## Storage

- **Images**: Stored in the `uploads/` directory with unique filenames
- **Database**: SQLite file `clinical_study.db` stores:
  - `id`: Unique record ID
  - `filename`: Stored image filename
  - `filepath`: Full path to the image
  - `result`: AI prediction label
  - `created_at`: Timestamp
