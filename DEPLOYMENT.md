# Deployment Guide

This guide will help you deploy the BSK Training Video Generator to various platforms.

## Pre-Deployment Checklist

- [ ] All API keys are set up (Google Gemini, Unsplash)
- [ ] Environment variables are configured
- [ ] Dependencies are installed and tested locally
- [ ] Application runs successfully with `streamlit run app.py`
- [ ] Required directories exist or will be created automatically:
  - `output_videos/`
  - `images/`
  - `generated_pdfs/`

## Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. Ensure your code is pushed to GitHub
2. Make sure `.env` is in `.gitignore` (it should be)
3. Verify `requirements.txt` is up to date

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Fill in the details:
   - **Repository**: Select your repository
   - **Branch**: Usually `main` or `master`
   - **Main file path**: `app.py`
5. Click "Advanced settings"
6. Add secrets (environment variables):
   ```
   GOOGLE_API_KEY=your_actual_gemini_api_key
   UNSPLASH_ACCESS_KEY=your_actual_unsplash_api_key
   ```
7. Click "Deploy"

### Step 3: Verify Deployment

- Check the logs for any errors
- Test video generation with a sample PDF or form
- Verify API keys are working

## Docker Deployment

### Build the Docker Image

```bash
docker build -t training-video-generator .
```

### Run the Container

```bash
docker run -d \
  -p 8501:8501 \
  -e GOOGLE_API_KEY=your_key \
  -e UNSPLASH_ACCESS_KEY=your_key \
  --name training-video-app \
  training-video-generator
```

### Access the Application

Open your browser to `http://localhost:8501`

## Heroku Deployment

### Prerequisites

1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login: `heroku login`

### Deploy

1. Create a Heroku app:
   ```bash
   heroku create your-app-name
   ```

2. Set environment variables:
   ```bash
   heroku config:set GOOGLE_API_KEY=your_key
   heroku config:set UNSPLASH_ACCESS_KEY=your_key
   ```

3. Deploy:
   ```bash
   git push heroku main
   ```

4. Open the app:
   ```bash
   heroku open
   ```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `UNSPLASH_ACCESS_KEY` | Yes | Unsplash API access key |
| `IMAGEMAGICK_BINARY` | No | Path to ImageMagick binary (if not in PATH) |

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify keys are set correctly in environment variables
   - Check that keys have proper permissions
   - Ensure no extra spaces in keys

2. **ImageMagick Errors**
   - For Docker: Already included in Dockerfile
   - For Streamlit Cloud: May need to install via `packages.txt`
   - For local: Install ImageMagick and add to PATH

3. **Video Generation Fails**
   - Check disk space availability
   - Verify `output_videos/` directory is writable
   - Check audio generation (Edge TTS) is working

4. **Memory Issues**
   - Video generation is memory-intensive
   - Consider increasing memory limits on your platform
   - Streamlit Cloud: Free tier has memory limits

### Streamlit Cloud Specific

- Maximum file upload: 200MB
- Memory limit: 1GB (free tier)
- Timeout: 60 seconds per request
- For larger videos, consider upgrading to Team tier

## Production Considerations

1. **Rate Limiting**: Implement rate limiting for API calls
2. **Caching**: Images are cached locally to reduce API calls
3. **Error Handling**: Comprehensive error handling is in place
4. **Logging**: Check Streamlit logs for debugging
5. **Monitoring**: Set up monitoring for API usage and errors

## Security Best Practices

- ✅ Never commit API keys to version control
- ✅ Use environment variables for all secrets
- ✅ Regularly rotate API keys
- ✅ Monitor API usage for unusual activity
- ✅ Use HTTPS in production

