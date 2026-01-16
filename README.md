# BSK Training Video Generator

An AI-powered video generator that creates professional training videos with slides, synthesized audio narration, and animated avatars. Built for Bangla Sahayta Kendra (BSK) data entry operator training.

## Features

- **AI-Powered Slide Generation**: Automatically generates structured training slides from PDF or form input using Google Gemini AI
- **Text-to-Speech**: Synthesizes natural-sounding narration using Microsoft Edge TTS
- **Dynamic Image Fetching**: Automatically fetches relevant images from Unsplash based on slide content
- **Professional Video Output**: Combines slides, audio, and animated avatar into polished training videos
- **PDF Support**: Upload PDF documents or fill out forms to generate training content
- **Streamlit Web Interface**: User-friendly web interface for easy video generation

## Installation

### Prerequisites

- Python 3.8 or higher
- ImageMagick (optional, only if not in system PATH)

### Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/training-video-generation.git
   cd training-video-generation
   ```

2. **Create Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   UNSPLASH_ACCESS_KEY=your_unsplash_api_key_here
   IMAGEMAGICK_BINARY=optional_path_to_magick.exe
   ```

   **Getting API Keys**:
   - **Google Gemini API**: Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Unsplash API**: Get your key from [Unsplash Developers](https://unsplash.com/developers)

5. **Install ImageMagick** (if not in PATH):
   - Download from [ImageMagick](https://imagemagick.org/script/download.php)
   - Add to system PATH or set `IMAGEMAGICK_BINARY` in `.env`

## Usage

### Running Locally

1. **Start the Streamlit App**:
   ```bash
   streamlit run app.py
   ```

2. **Generate a Video**:
   - Navigate to "🎬 Create New Video" page
   - Either upload a PDF or fill out the service training form
   - Select narrator voice from sidebar
   - Click "🚀 Generate Training Video"
   - Wait for processing and download your video

### Deployment to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository and branch
   - Set main file path: `app.py`
   - Add your secrets (API keys) in the Secrets section:
     ```
     GOOGLE_API_KEY=your_gemini_api_key
     UNSPLASH_ACCESS_KEY=your_unsplash_api_key
     ```
   - Click "Deploy"

3. **Environment Variables**:
   Streamlit Cloud uses the Secrets section instead of `.env` files. Add your API keys there.

### Deployment to Other Platforms

#### Heroku

1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS=false\n\
   " > ~/.streamlit/config.toml
   ```

3. Set environment variables in Heroku dashboard

#### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t training-video-generator .
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_key -e UNSPLASH_ACCESS_KEY=your_key training-video-generator
```

## Project Structure

```
training-video-generation/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── services/
│   ├── gemini_service.py  # Google Gemini AI integration
│   ├── openai_service.py  # OpenAI service (if used)
│   └── unsplash_service.py # Unsplash image API
├── utils/
│   ├── audio_utils.py     # Text-to-speech utilities
│   ├── avatar_utils.py   # Avatar animation utilities
│   ├── image_utils.py    # Image processing utilities
│   ├── pdf_extractor.py  # PDF content extraction
│   ├── pdf_utils.py      # PDF generation utilities
│   ├── service_utils.py  # Service validation utilities
│   └── video_utils.py    # Video generation utilities
├── assets/
│   ├── avatar/           # Avatar images
│   ├── logo.png         # Logo files
│   └── style.css        # Custom CSS
├── images/              # Cached Unsplash images
├── output_videos/       # Generated video files
└── generated_pdfs/      # Generated PDF documents
```

## Architecture Overview

1. **Input**: User provides PDF or fills out form with service training information
2. **Content Extraction**: PDF content is extracted or form data is structured
3. **AI Slide Generation**: Google Gemini AI structures content into training slides
4. **Image Fetching**: Unsplash API fetches relevant images for each slide
5. **Audio Synthesis**: Edge TTS converts slide narration to speech
6. **Video Assembly**: MoviePy combines slides, audio, and avatar into final video
7. **Output**: Professional training video ready for download

## Technologies Used

- **Python 3.8+**: Core programming language
- **Streamlit**: Web application framework
- **Google Gemini AI**: Slide content generation and structuring
- **Microsoft Edge TTS**: Text-to-speech synthesis
- **Unsplash API**: Image fetching service
- **MoviePy**: Video editing and composition
- **Pillow**: Image processing
- **PyMuPDF**: PDF content extraction
- **ReportLab**: PDF generation
- **ImageMagick**: Image manipulation (optional)

## Configuration

The application uses environment variables for configuration:

- `GOOGLE_API_KEY`: Required - Google Gemini API key
- `UNSPLASH_ACCESS_KEY`: Required - Unsplash API access key
- `IMAGEMAGICK_BINARY`: Optional - Path to ImageMagick binary if not in PATH

## Troubleshooting

### ImageMagick Issues
- If you get ImageMagick errors, ensure it's installed and in your PATH
- Or set `IMAGEMAGICK_BINARY` environment variable to the full path

### API Key Errors
- Ensure all required API keys are set in `.env` file or environment variables
- Check that keys are valid and have proper permissions

### Video Generation Fails
- Check that `output_videos/` directory exists and is writable
- Ensure sufficient disk space for video files
- Check audio file generation is working (Edge TTS)

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
