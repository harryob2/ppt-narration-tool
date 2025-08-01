# PowerPoint Narration Tool

A web application that allows users to upload PowerPoint presentations and audio files to create narrated presentations.

## Features

- Upload PowerPoint (.pptx) files
- Upload audio files (.mp3, .m4a, .wav)
- Automatically embed audio files into slides based on filename (e.g., "1.mp3" goes to slide 1)
- Download the narrated PowerPoint file

## Deployment on Vercel

This application is configured for deployment on Vercel's serverless platform.

### Prerequisites

- Vercel account
- Python 3.11

### Deployment Steps

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy to Vercel:
   ```bash
   vercel
   ```

3. Follow the prompts to link your project and deploy.

### Troubleshooting

If you encounter a "FUNCTION_INVOCATION_FAILED" error:

1. Check the Vercel function logs in the dashboard
2. Ensure all dependencies are listed in `requirements.txt`
3. Verify the file size limits (max 50MB)
4. Check that the `static` and `templates` folders are in the `api` directory

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python api/app.py
   ```

3. Open http://localhost:5000 in your browser

## File Structure

```
├── api/
│   ├── app.py          # Main Flask application
│   ├── templates/      # HTML templates
│   └── static/         # Static files (CSS, images)
├── requirements.txt    # Python dependencies
├── vercel.json        # Vercel configuration
└── README.md          # This file
```

## Usage

1. Upload your PowerPoint presentation
2. Upload audio files named according to slide numbers (e.g., "1.mp3", "2.wav")
3. Click "Submit" to process the files
4. Download your narrated PowerPoint

## Notes

- Audio files should be named with the slide number (e.g., "1.mp3" for slide 1)
- Only .pptx, .mp3, .m4a, and .wav files are supported
- Maximum file size is 50MB
- Files are processed in memory for serverless compatibility
