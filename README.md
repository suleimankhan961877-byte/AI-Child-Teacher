# Learnora AI

Learnora AI is a Python + Streamlit educational prototype that uses Groq to generate:
- age-appropriate lesson plans
- multilingual teacher scripts
- scene-by-scene visual prompts
- examples and short quizzes
- downloadable 1280×720 MP4 educational animations
- optional teacher voice using local `edge-tts`

## Important architecture note

Groq provides the AI lesson/storyboard and teacher narration text. It is not a video-generation API. This project therefore renders the animation locally with Pillow + FFmpeg. This keeps the video pipeline inexpensive and avoids pretending that the Groq API itself generates video.

## Files

- `app.py` — main Streamlit application
- `requirements.txt` — Python dependencies
- `.env.example` — API-key template

## 1. Install Python

Use Python 3.10+.

## 2. Install packages

```bash
pip install -r requirements.txt
```

## 3. Install FFmpeg

FFmpeg must be installed separately and available on your PATH.

Verify:

```bash
ffmpeg -version
```

## 4. Create Groq API key

Create a Groq API key from the Groq console.

You can either:
- enter the key in the app sidebar, or
- set the `GROQ_API_KEY` environment variable.

Do not commit a real API key to GitHub.

## 5. Run

```bash
streamlit run app.py
```

## 6. Workflow

1. Enter a topic.
2. Select child age.
3. Select one or more teaching languages.
4. Select Simple / Medium / Advanced.
5. Select Short / Medium / Long.
6. Choose an animation style.
7. Click **Generate AI Lesson**.
8. Review every scene and the teacher narration.
9. Click **Render HD Video**.
10. Download the MP4.
11. Generate optional teacher voice.
12. Download the video with voice.
13. If the animation does not fit, enter an animation change request and regenerate.

## Production upgrade path

For truly generative high-resolution images/video rather than local illustrated slides, connect a dedicated image/video generation service to the `visual_prompt` field. Keep Groq as the lesson-planning/orchestration model.

The current app intentionally has no hard-coded image/video vendor, so you can add one later without changing the educational workflow.
