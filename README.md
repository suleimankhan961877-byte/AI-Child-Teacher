# Learnora AI — Fixed Video Engine

This version fixes the `FFmpeg is not installed or is not on PATH` problem.

## What changed

The application now:
- checks whether FFmpeg is already installed;
- automatically uses the FFmpeg binary supplied by `imageio-ffmpeg` when system FFmpeg is unavailable;
- uses the same automatic FFmpeg resolver when adding teacher narration;
- keeps the video output at 1280×720;
- uses `openai/gpt-oss-120b` instead of the deprecated `llama-3.3-70b-versatile`.

## Installation

Open Command Prompt/PowerShell in the project folder:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Then start Streamlit:

```bash
python -m streamlit run app.py
```

You normally do NOT need to install FFmpeg separately.

If automatic FFmpeg setup fails, run:

```bash
python -m pip install --upgrade imageio-ffmpeg
```

and restart Streamlit.

## Groq

Enter your Groq API key in the application sidebar, or set:

```text
GROQ_API_KEY=your_key_here
```

Do not publish a real API key in GitHub.

## Video workflow

1. Generate the lesson.
2. Review scenes and narration.
3. Click **Render HD Video**.
4. The app generates the illustrated MP4.
5. Generate teacher voice if desired.
6. Download the MP4 with narration.
