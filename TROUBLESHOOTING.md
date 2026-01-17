# BSK Training Video Generator - Troubleshooting Guide

## Quick Fix Summary

### Problem: Blank Output When Generating New Version

**Root Cause:** The application was using `return` instead of `st.stop()` when showing version confirmation dialogs, which caused the script to exit prematurely.

**Fixed Issues:**
1. ✅ Changed `return` to `st.stop()` in version confirmation dialogs
2. ✅ Added unique button keys to prevent duplicate widget ID errors
3. ✅ Added comprehensive error handling and logging
4. ✅ Added better status messages during video generation
5. ✅ Added validation to ensure video clips are created before rendering

## How to Use the Fixed Version

### Starting the Application

**Option 1: Using the Startup Script (Recommended)**
```bash
# Double-click on start_app.bat
# OR run from command prompt:
start_app.bat
```

**Option 2: Manual Start**
```bash
# Navigate to project directory
cd C:\Users\AICOE\Downloads\train-video-main\train-video-main

# Run the app
py -m streamlit run app.py
```

### Testing the Fix

1. **Run Diagnostic Test**
   ```bash
   py debug_version_test.py
   ```
   This will check:
   - Registry file status
   - Existing services
   - Output directory
   - Dependencies

2. **Generate a New Version**
   - Upload a PDF or fill the form
   - Click "Generate Training Video"
   - If an existing version is detected:
     - You'll see a confirmation dialog
     - Click "✅ Generate New Version"
     - **Important:** The video generation should now proceed immediately
     - You should see progress messages like:
       - 🧠 Structuring training slides using AI...
       - 🎬 Creating slide X of Y...
       - 🎙️ Generating narration audio...
       - 🎞️ Rendering final video...

## Expected Behavior After Fix

### Version Control Flow

1. **First Time Generation**
   - Status: `NEW_SERVICE`
   - Creates version 1.0
   - No confirmation needed

2. **Same Content**
   - Status: `UP_TO_DATE`
   - Shows info message
   - Proceeds with same version

3. **Updated Content**
   - Status: `UPDATE_NEEDED`
   - Shows confirmation dialog
   - **After clicking "Generate New Version":**
     - Clears the dialog (progress bar and status)
     - Shows: "🔄 Generating Version X.Y..."
     - Immediately starts video generation
     - Shows detailed progress for each slide
     - Completes with success message and balloons

## Common Issues and Solutions

### Issue 1: Video Not Generating After Confirmation

**Symptoms:**
- Click "Generate New Version"
- Dialog disappears
- No progress shown
- Page refreshes to initial state

**Solution:**
✅ **FIXED** - The app now uses `st.stop()` instead of `return`, and properly continues the generation flow after confirmation.

**Verification:**
- You should see "🔄 Generating Version X.Y..." immediately after clicking
- Progress bar should appear
- Status messages should show slide-by-slide progress

### Issue 2: Duplicate Key Errors

**Symptoms:**
- Red error message about duplicate widget keys
- `DuplicateWidgetID` exception

**Solution:**
✅ **FIXED** - Button keys now include file hash to ensure uniqueness: `form_update_btn_{file_hash[:8]}`

### Issue 3: Silent Failures

**Symptoms:**
- No error messages
- Video generation seems to work but produces nothing
- No feedback about what went wrong

**Solution:**
✅ **FIXED** - Added comprehensive error handling:
- Try-catch blocks around each slide generation
- Logging for all major operations
- User-friendly error messages
- Validation before final rendering

### Issue 4: Missing Dependencies

**Symptoms:**
- Import errors
- Module not found errors

**Solution:**
```bash
# Install all required packages
py -m pip install -r requirements.txt

# Or install individually:
py -m pip install streamlit moviepy pillow edge-tts google-generativeai requests
```

**Verification:**
```bash
py debug_version_test.py
```
Check the "[6] Checking Dependencies..." section.

## File Structure Check

Ensure these files exist:
```
train-video-main/
├── app.py (UPDATED)
├── debug_version_test.py (NEW)
├── start_app.bat (NEW)
├── TROUBLESHOOTING.md (NEW)
├── version_registry.json (created after first video)
├── output_videos/
│   └── (generated videos)
├── generated_pdfs/
│   └── (generated PDFs)
├── utils/
│   ├── version_utils.py
│   ├── video_utils.py
│   └── ...
└── services/
    ├── gemini_service.py
    └── ...
```

## Environment Variables

Make sure these are set (if using API keys):

```bash
# For Gemini AI
GOOGLE_API_KEY=your_api_key_here

# For Unsplash (optional)
UNSPLASH_ACCESS_KEY=your_key_here
```

## Debugging Steps

### Step 1: Check System Status
```bash
py debug_version_test.py
```

### Step 2: Review Logs
Check console output for:
- ✅ Success messages (green)
- ⚠️ Warnings (yellow)
- ❌ Errors (red)

### Step 3: Verify Registry
```bash
# View registry content
type version_registry.json
```

Should show:
```json
{
  "services": {
    "service_name": {
      "current_version": "1.0",
      "video_path": "output_videos/...",
      ...
    }
  },
  ...
}
```

### Step 4: Test Individual Components

**Test Audio Generation:**
```python
import asyncio
from utils.audio_utils import text_to_speech

audio = asyncio.run(text_to_speech("Test narration", voice="en-IN-NeerjaNeural"))
print(f"Audio generated: {audio}")
```

**Test Image Fetching:**
```python
from services.unsplash_service import fetch_and_save_photo

image = fetch_and_save_photo("government office")
print(f"Image saved: {image}")
```

## Performance Tips

1. **Slide Count:** Optimal is 5-8 slides
2. **Audio Duration:** Keep narration under 30 seconds per slide
3. **Image Quality:** Default settings work best
4. **Concurrent Generations:** Run one at a time

## Version History

### v1.1 (Current - Fixed)
- ✅ Fixed blank output on version generation
- ✅ Added proper error handling
- ✅ Improved user feedback
- ✅ Added diagnostic tools

### v1.0 (Original)
- ❌ Used `return` in confirmation dialogs
- ❌ Missing error context
- ❌ Silent failures possible

## Getting Help

If issues persist:

1. **Run full diagnostic:**
   ```bash
   py debug_version_test.py > diagnostic_output.txt
   ```

2. **Check logs:**
   - Console output from Streamlit
   - Error messages in red
   - Warning messages in yellow

3. **Verify fixes applied:**
   ```bash
   # Search for st.stop() instead of return
   findstr /n "st.stop()" app.py
   ```

4. **Clean start:**
   ```bash
   # Delete registry and try fresh
   del version_registry.json
   py -m streamlit run app.py
   ```

## Success Indicators

✅ **System Working Correctly:**
- Debug script shows all green checkmarks
- "Generate New Version" shows immediate progress
- Video file created in output_videos/
- Registry updated with version info
- Success message with balloons 🎈

## Contact

For persistent issues, provide:
1. Output from `py debug_version_test.py`
2. Console error messages
3. Content of version_registry.json
4. Steps to reproduce the issue
