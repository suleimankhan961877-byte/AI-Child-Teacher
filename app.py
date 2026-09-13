import os
import io
import json
import base64
import tempfile
import subprocess
from pathlib import Path

import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont

APP_NAME = "Learnora AI"
OUTPUT_DIR = Path(tempfile.gettempdir()) / "learnora_ai"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="Learnora AI — AI Teacher",
    page_icon="🎓",
    layout="wide",
)

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#f7fbff 0%,#fff8fb 55%,#f7fff9 100%);}
.hero {
    padding: 28px; border-radius: 24px; margin-bottom: 22px;
    background: linear-gradient(120deg,#5b5ce2,#8b5cf6,#ec4899);
    color:white; box-shadow: 0 12px 35px rgba(70,60,150,.18);
}
.hero h1 {font-size: 42px; margin:0;}
.card {padding:18px; border-radius:18px; background:white;
       border:1px solid #e8e8f2; box-shadow:0 5px 18px rgba(0,0,0,.05);}
.small {color:#667085; font-size:14px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🎓 Learnora AI</h1>
<p style="font-size:18px">A friendly AI teacher that turns a topic into a clear lesson, illustrated scenes, narration and a downloadable MP4.</p>
</div>
""", unsafe_allow_html=True)

def get_client():
    key = st.session_state.get("groq_key") or os.getenv("GROQ_API_KEY")
    if not key:
        return None
    return Groq(api_key=key)

def groq_text(prompt, system):
    client = get_client()
    if client is None:
        raise RuntimeError("Please enter your Groq API key in the sidebar.")
    result = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_completion_tokens=5000,
    )
    return result.choices[0].message.content

def clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n",1)[1]
        text = text.rsplit("```",1)[0]
    return json.loads(text)

def make_lesson(topic, age, languages, level, duration, animation_style, feedback=""):
    seconds = {"Short": 30, "Medium": 60, "Long": 100}[duration]
    scenes = {"Short": 5, "Medium": 8, "Long": 12}[duration]
    prompt = f"""
Create a child-friendly multimedia lesson plan.

Topic: {topic}
Child age: {age}
Teaching languages: {", ".join(languages)}
Study level: {level}
Duration target: about {seconds} seconds
Number of scenes: {scenes}
Animation style: {animation_style}
Previous animation feedback: {feedback or "none"}

Return ONLY valid JSON with this structure:
{{
 "title": "...",
 "learning_objective": "...",
 "teacher_intro": "...",
 "scenes": [
   {{
     "scene": 1,
     "heading": "...",
     "visual_prompt": "...",
     "on_screen_text": "...",
     "teacher_narration": "...",
     "example": "..."
   }}
 ],
 "quiz": [
   {{"question":"...","answer":"..."}}
 ]
}}

Rules:
- Explain every important idea step by step.
- Use simple, age-appropriate language.
- Keep visual prompts safe, colorful, educational and easy to understand.
- Narration must be natural spoken language.
- Include concrete examples.
- Do not put markdown outside JSON.
"""
    return clean_json(groq_text(
        prompt,
        "You are an expert primary-school teacher, instructional designer and animation storyboard writer."
    ))

def load_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = str(text).split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if draw.textbbox((0,0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def make_scene_image(scene, index, total, style):
    w, h = 1280, 720
    img = Image.new("RGB", (w,h), (245,248,255))
    d = ImageDraw.Draw(img)

    # Bright educational abstract background
    d.rounded_rectangle((45,45,w-45,h-45), radius=35, fill=(255,255,255))
    d.ellipse((850,90,1180,420), fill=(230,236,255))
    d.ellipse((930,330,1220,620), fill=(255,232,245))
    d.rounded_rectangle((90,95,790,145), radius=20, fill=(232,239,255))

    title_font = load_font(38)
    body_font = load_font(30)
    small_font = load_font(22)

    d.text((110,108), f"{scene.get('heading','Lesson')}   •   {index}/{total}",
           font=title_font, fill=(38,47,82))

    visual = scene.get("visual_prompt","Educational illustration")
    text = scene.get("on_screen_text","")
    example = scene.get("example","")

    # Simple graphic: central concept card + decorative shapes
    d.rounded_rectangle((120,190,760,500), radius=30, fill=(247,250,255), outline=(210,218,240), width=3)
    visual_lines = wrap_text(d, visual, body_font, 570)
    y = 220
    for line in visual_lines[:7]:
        d.text((155,y), line, font=body_font, fill=(55,65,95))
        y += 42

    d.rounded_rectangle((820,160,1160,300), radius=25, fill=(255,248,220))
    d.text((850,180), "KEY IDEA", font=small_font, fill=(110,85,20))
    for i, line in enumerate(wrap_text(d, text, body_font, 280)[:4]):
        d.text((850,220+i*38), line, font=body_font, fill=(60,55,40))

    d.rounded_rectangle((820,345,1160,540), radius=25, fill=(232,250,239))
    d.text((850,365), "EXAMPLE", font=small_font, fill=(25,90,55))
    for i, line in enumerate(wrap_text(d, example, body_font, 280)[:5]):
        d.text((850,405+i*38), line, font=body_font, fill=(40,75,55))

    d.text((110,620), f"Style: {style}", font=small_font, fill=(100,110,130))
    return img

def create_slideshow_video(lesson, style, fps=12):
    # Uses FFmpeg when available. Produces a real MP4 from generated HD slide graphics.
    ffmpeg = "ffmpeg"
    if os.name == "nt":
        # ffmpeg.exe must be on PATH; otherwise show a clear message.
        ffmpeg = "ffmpeg"

    scene_files = []
    total = len(lesson["scenes"])
    for i, scene in enumerate(lesson["scenes"], 1):
        img = make_scene_image(scene, i, total, style)
        path = OUTPUT_DIR / f"scene_{i:02d}.png"
        img.save(path, "PNG", optimize=True)
        scene_files.append(path)

    concat = OUTPUT_DIR / "concat.txt"
    # Give each scene an equal visual duration.
    with concat.open("w", encoding="utf-8") as f:
        for p in scene_files:
            f.write(f"file '{p.as_posix()}'\n")
            f.write("duration 5\n")
        f.write(f"file '{scene_files[-1].as_posix()}'\n")

    out = OUTPUT_DIR / "learnora_lesson.mp4"
    cmd = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat),
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-r", str(fps), "-c:v", "libx264", "-preset", "medium",
        "-crf", "18", "-movflags", "+faststart", str(out)
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return out
    except FileNotFoundError:
        raise RuntimeError("FFmpeg is not installed or is not on PATH. Install FFmpeg, restart the terminal, then run the app again.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("FFmpeg could not create the MP4. Check that FFmpeg has H.264/libx264 support.")

def create_voice_audio(text, voice="en"):
    # Optional local narration using edge-tts. This is not a Groq capability.
    try:
        import edge_tts
    except ImportError:
        return None

    voice_map = {
        "English": "en-US-AriaNeural",
        "Urdu": "ur-PK-UzmaNeural",
        "Hindi": "hi-IN-SwaraNeural",
        "Arabic": "ar-SA-ZariyahNeural",
        "Spanish": "es-ES-ElviraNeural",
        "French": "fr-FR-DeniseNeural",
    }
    chosen = voice_map.get(voice, "en-US-AriaNeural")
    audio = OUTPUT_DIR / f"narration_{voice.lower()}.mp3"
    try:
        import asyncio
        async def run():
            await edge_tts.Communicate(text, chosen).save(str(audio))
        asyncio.run(run())
        return audio if audio.exists() else None
    except Exception:
        return None

def attach_audio(video_path, audio_path):
    out = OUTPUT_DIR / "learnora_lesson_with_voice.mp4"
    cmd = [
        "ffmpeg","-y","-i",str(video_path),"-i",str(audio_path),
        "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac",
        "-shortest","-movflags","+faststart",str(out)
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return out
    except Exception:
        return video_path

with st.sidebar:
    st.header("🔐 Groq API")
    key = st.text_input("Groq API key", type="password",
                        value=st.session_state.get("groq_key",""),
                        help="Your key is used only for this app session.")
    if key:
        st.session_state["groq_key"] = key
    st.caption("Groq is used for lesson planning and teacher narration text. Video rendering is performed locally.")

st.subheader("1. Build your lesson")
c1, c2 = st.columns(2)
with c1:
    topic = st.text_input("📚 Topic", placeholder="e.g., The Solar System")
    age = st.number_input("👧 Child age", min_value=3, max_value=17, value=7)
    languages = st.multiselect("🌍 Teaching language(s)",
                               ["English","Urdu","Hindi","Arabic","Spanish","French"],
                               default=["English"])
with c2:
    level = st.selectbox("🎯 Study level", ["Simple","Medium","Advanced"])
    duration = st.selectbox("⏱️ Teaching duration", ["Short","Medium","Long"])
    style = st.selectbox("🎨 Animation style",
                         ["Colorful cartoon","Storybook","Science classroom",
                          "Playful 2D infographic","Space adventure"])

feedback = st.text_area(
    "🔄 Optional animation change request",
    placeholder="If the previous animation did not fit, describe what should change..."
)

generate = st.button("✨ Generate AI Lesson", type="primary", use_container_width=True)

if generate:
    if not topic.strip():
        st.error("Please enter a topic.")
    else:
        try:
            with st.spinner("Creating your lesson plan, scenes and teacher script..."):
                lesson = make_lesson(topic, age, languages, level, duration, style, feedback)
            st.session_state["lesson"] = lesson
            st.session_state["style"] = style
            st.success("Lesson created successfully.")
        except Exception as e:
            st.error(str(e))

lesson = st.session_state.get("lesson")
if lesson:
    st.divider()
    st.subheader(f"📖 {lesson.get('title','Lesson')}")
    st.write("**Learning objective:**", lesson.get("learning_objective",""))

    for scene in lesson["scenes"]:
        with st.expander(f"Scene {scene['scene']}: {scene['heading']}"):
            st.write("**Visual:**", scene["visual_prompt"])
            st.write("**On-screen:**", scene["on_screen_text"])
            st.write("**Teacher:**", scene["teacher_narration"])
            st.write("**Example:**", scene["example"])

    st.subheader("🎬 Create downloadable HD animation")
    st.info("The current version creates a 1280×720 MP4 slideshow with illustrated graphics. The narration script is generated by Groq. Optional local text-to-speech can add teacher voice.")

    if st.button("🎥 Render HD Video", type="primary"):
        try:
            with st.spinner("Rendering HD MP4..."):
                video = create_slideshow_video(lesson, st.session_state["style"])
            st.session_state["video"] = str(video)
            st.success("Video rendered.")
        except Exception as e:
            st.error(str(e))

    video_path = st.session_state.get("video")
    if video_path and Path(video_path).exists():
        st.video(video_path)
        with open(video_path, "rb") as f:
            st.download_button("⬇️ Download HD MP4", f, "learnora_lesson.mp4", "video/mp4",
                               use_container_width=True)

    st.subheader("🗣️ Teacher voice")
    voice_language = st.selectbox("Voice language", languages, key="voice_language")
    all_script = "\n\n".join(s["teacher_narration"] for s in lesson["scenes"])
    st.text_area("Complete teacher narration", all_script, height=220)

    if st.button("🔊 Generate Teacher Voice"):
        audio = create_voice_audio(all_script, voice_language)
        if audio:
            st.session_state["audio"] = str(audio)
            st.audio(audio)
            with open(audio, "rb") as f:
                st.download_button("⬇️ Download Teacher Voice", f,
                                   "teacher_narration.mp3", "audio/mpeg")
            if st.session_state.get("video"):
                with st.spinner("Adding narration to the video..."):
                    final_video = attach_audio(Path(st.session_state["video"]), audio)
                st.session_state["final_video"] = str(final_video)
        else:
            st.warning("Optional voice package is unavailable or the selected voice could not be generated. The complete teacher script is still available for download.")

    final_video = st.session_state.get("final_video")
    if final_video and Path(final_video).exists():
        st.video(final_video)
        with open(final_video, "rb") as f:
            st.download_button("⬇️ Download Video + Teacher Voice", f,
                               "learnora_lesson_with_voice.mp4", "video/mp4",
                               use_container_width=True)

    st.subheader("🔄 Improve the animation")
    st.write("Change the style or describe what does not fit, then press **Generate AI Lesson** again. The revised storyboard and visuals will be regenerated.")

    st.subheader("📝 Quick check")
    for q in lesson.get("quiz", []):
        st.markdown(f"**Q:** {q['question']}")
        st.caption(f"Answer: {q['answer']}")

st.divider()
st.caption("Learnora AI • Python + Streamlit + Groq • Educational prototype")
