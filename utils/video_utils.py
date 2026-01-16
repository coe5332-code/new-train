from utils.avatar_utils import add_avatar_to_slide
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import (
    ImageClip, concatenate_videoclips, CompositeVideoClip,
    AudioFileClip, concatenate_audioclips, ColorClip, vfx
)

VIDEO_W, VIDEO_H = 1280, 720
TOP_TEXT_HEIGHT = int(VIDEO_H * 0.6)
BOTTOM_IMAGE_HEIGHT = VIDEO_H - TOP_TEXT_HEIGHT


# -------------------------------------------------
# TEXT RENDERING WITH PIL (NO IMAGEMAGICK NEEDED)
# -------------------------------------------------
def create_text_image(text, fontsize, color, max_width, font_name="Arial", bold=False):
    """
    Create a text image using PIL (no ImageMagick required).
    Returns a temporary file path with the rendered text image.
    """
    # Try to load font, fallback to default if not available
    try:
        if bold:
            # Try bold font
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "C:/Windows/Fonts/arialbd.ttf",  # Windows
            ]
        else:
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "C:/Windows/Fonts/arial.ttf",  # Windows
            ]
        
        font = None
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, fontsize)
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Parse color
    if isinstance(color, str):
        color_map = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "lightgray": (211, 211, 211),
            "gray": (128, 128, 128),
        }
        rgb_color = color_map.get(color.lower(), (255, 255, 255))
    else:
        rgb_color = color
    
    # Create image with transparent background
    # Start with a reasonable size, we'll crop later
    img = Image.new("RGBA", (max_width, fontsize * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Word wrap text
    words = text.split()
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        # Estimate width (approximate)
        word_width = len(word) * fontsize * 0.6
        if current_width + word_width > max_width and current_line:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width + fontsize * 0.3
    
    if current_line:
        lines.append(" ".join(current_line))
    
    # Draw text
    y_offset = 0
    line_height = int(fontsize * 1.2)
    for line in lines:
        draw.text((0, y_offset), line, fill=rgb_color, font=font)
        y_offset += line_height
    
    # Crop to actual text size
    bbox = img.getbbox()
    if bbox:
        img = img.crop((0, 0, max_width, bbox[3] + 10))
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_file.name, "PNG")
    temp_file.close()
    
    return temp_file.name


def create_text_clip(text, fontsize, color, max_width, position, start_time, duration, fadein=0, font_name="Arial", bold=False, opacity=1.0):
    """
    Create a MoviePy ImageClip from PIL-rendered text.
    This replaces TextClip and doesn't require ImageMagick.
    """
    text_img_path = create_text_image(text, fontsize, color, max_width, font_name, bold)
    
    clip = ImageClip(text_img_path)
    clip = clip.set_position(position)
    clip = clip.set_start(start_time)
    clip = clip.set_duration(duration)
    clip = clip.set_opacity(opacity)
    
    if fadein > 0:
        clip = clip.fadein(fadein)
    
    return clip


# -------------------------------------------------
# SLIDE CREATION WITH BETTER ANIMATION
# -------------------------------------------------
def create_slide(title, points, image_path, audio_file):
    if not os.path.exists(audio_file) or os.path.getsize(audio_file) < 1024:
        raise RuntimeError(f"Invalid audio file: {audio_file}")
    audio_clip = AudioFileClip(audio_file)
    duration = audio_clip.duration + 0.4  # small buffer

    # -----------------------------
    # BACKGROUND (soft animated)
    # -----------------------------
    bg = (
        ColorClip(size=(VIDEO_W, VIDEO_H), color=(20, 22, 32))
        .set_duration(duration)
        .fx(vfx.fadein, 0.4)
        .fx(vfx.fadeout, 0.4)
    )

    overlay = (
        ColorClip(size=(VIDEO_W, VIDEO_H), color=(0, 0, 0))
        .set_opacity(0.35)
        .set_duration(duration)
    )

    # -----------------------------
    # TITLE (using PIL instead of TextClip)
    # -----------------------------
    title_clip = create_text_clip(
        title,
        fontsize=48,
        color="white",
        max_width=VIDEO_W - 120,
        position=("center", 50),
        start_time=0.2,
        duration=duration,
        fadein=0.6,
        bold=True
    )

    title_shadow = create_text_clip(
        title,
        fontsize=48,
        color="black",
        max_width=VIDEO_W - 120,
        position=("center", 52),
        start_time=0.2,
        duration=duration,
        opacity=0.6,
        bold=True
    )

    # -----------------------------
    # BULLETS (top section only)
    # -----------------------------
    bullet_clips = []
    start_y = 140
    line_gap = 44

    for i, point in enumerate(points[:5]):
        appear_time = 0.8 + i * 0.5
        text = f"• {point.strip()}"

        shadow = create_text_clip(
            text,
            fontsize=32,
            color="black",
            max_width=VIDEO_W - 200,
            position=(102, start_y + i * line_gap + 2),
            start_time=appear_time,
            duration=duration - appear_time,
            opacity=0.5
        )

        bullet = create_text_clip(
            text,
            fontsize=32,
            color="white",
            max_width=VIDEO_W - 200,
            position=(100, start_y + i * line_gap),
            start_time=appear_time,
            duration=duration - appear_time,
            fadein=0.4
        )

        bullet_clips.extend([shadow, bullet])


    # -----------------------------
    # CONTENT IMAGE (BOTTOM-RIGHT, STATIC)
    # -----------------------------
    image_clips = []
    if os.path.exists(image_path):
        img = (
            ImageClip(image_path)
            .resize(height=220)  # fixed, clean size
            .set_position((
                VIDEO_W - 260,    # right margin
                VIDEO_H - 260     # bottom margin
            ))
            .set_duration(duration)
        )

        image_clips.append(img)


    # -----------------------------
    # FOOTER
    # -----------------------------
    footer = create_text_clip(
        "Bangla Sahayta Kendra • Government of West Bengal",
        fontsize=18,
        color="lightgray",
        max_width=VIDEO_W - 80,
        position=("center", VIDEO_H - 40),
        start_time=0,
        duration=duration
    )

    slide = CompositeVideoClip(
        [bg, overlay, title_shadow, title_clip]
        + bullet_clips
        + image_clips
        + [footer],
        size=(VIDEO_W, VIDEO_H)
    ).set_duration(duration)

    slide = slide.set_audio(audio_clip)

    # -----------------------------
    # AVATAR (kept intact)
    # -----------------------------
    slide = add_avatar_to_slide(slide, audio_clip.duration)

    return slide.crossfadein(0.4).crossfadeout(0.4)


# -------------------------------------------------
# COMBINE SLIDES (NO BLACK GAPS)
# -------------------------------------------------
def combine_slides_and_audio(video_clips, audio_paths, service_name=None):
    # Smooth overlap between slides
    final_video = concatenate_videoclips(
        video_clips,
        method="compose",
        padding=-0.4
    )

    audio_clips = [AudioFileClip(p) for p in audio_paths]
    final_audio = concatenate_audioclips(audio_clips)

    final_video = final_video.set_audio(final_audio)

    os.makedirs("output_videos", exist_ok=True)

    filename = "bsk_training_video.mp4"
    if service_name:
        safe = service_name.replace(" ", "_")
        filename = f"BSK_Training_{safe}.mp4"

    output_path = os.path.join("output_videos", filename)

    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=30,
        preset="medium",
        bitrate="2000k",
        threads=4
    )

    return output_path
