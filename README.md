<div align="center">

<img src="docs/screenshots/banner.png" alt="Guitar Tutor AI Banner" width="100%"/>

# 🎸 Guitar Tutor AI

### *Master Music with Intelligent Feedback*

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

[![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-FF6B6B?style=flat-square&logo=socketdotio)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlite)](https://sqlalchemy.org)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-412991?style=flat-square&logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![Framer Motion](https://img.shields.io/badge/Framer_Motion-Animations-0055FF?style=flat-square&logo=framer)](https://framer.com/motion)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)

<br/>

**An intelligent, full-stack guitar tutoring platform powered by Machine Learning, LLMs, and real-time audio analysis.**

[🚀 Getting Started](#-installation) · [📖 Docs](#-api-documentation) · [🖼️ Screenshots](#-screenshots) · [🤝 Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Running the Project](#-running-the-project)
- [API Documentation](#-api-documentation)
- [Screenshots](#-screenshots)
- [Future Enhancements](#-future-enhancements)
- [Performance Highlights](#-performance-highlights)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)
- [Acknowledgements](#-acknowledgements)

---

## 🌟 Overview

**Guitar Tutor AI** is a production-grade, AI-powered guitar learning platform that transforms how musicians practice. It listens to your guitar playing in real-time, detects chords, analyzes notes and strumming patterns, transcribes your speech questions, and gives you intelligent, voice-assisted feedback — all through a sleek, modern chat interface.

> 💡 **Think of it as having a personal guitar teacher available 24/7, powered by AI.**

This project combines:
- 🎵 **Advanced audio processing** (Demucs, Librosa, Madmom)
- 🗣️ **Speech recognition** (OpenAI Whisper)
- 🤖 **Large Language Models** (LM Studio — fully local, private)
- 🔊 **Text-to-Speech** (Piper TTS — offline voice synthesis)
- 🌐 **Modern full-stack web application** (React + FastAPI + WebSockets)

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🎵 Audio Intelligence
- **Real-time chord detection** using Madmom deep learning
- **Note-by-note analysis** via Librosa pitch estimation
- **Strumming pattern recognition** with BPM + D/U stroke breakdown
- **Source separation** — isolates guitar from mixed audio using Demucs

</td>
<td width="50%">

### 🤖 AI & Voice
- **Whisper STT** — transcribes your spoken questions
- **Local LLM feedback** via LM Studio (fully private, no cloud)
- **Piper TTS** — natural voice responses, works offline
- **Contextual AI guidance** with music theory explanations

</td>
</tr>
<tr>
<td width="50%">

### 💻 Full-Stack Platform
- **WebSocket real-time pipeline** — sub-second response loop
- **JWT authentication** with secure session management
- **Chat history** with per-session message persistence
- **FastAPI REST APIs** with auto-generated Swagger docs

</td>
<td width="50%">

### 🎨 Premium UI/UX
- **Glassmorphism dark UI** with dynamic ambient gradients
- **Animated chat interface** inspired by modern AI assistants
- **Responsive React dashboard** with Framer Motion animations
- **shadcn/ui + Radix** for accessible, polished components

</td>
</tr>
</table>

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph Client["🖥️ React Frontend (Vite + TypeScript)"]
        UI[Chat Interface]
        Mic[Microphone Input]
        Audio[Audio Upload]
    end

    subgraph Gateway["⚡ FastAPI Gateway (Port 8000)"]
        WS["WebSocket /ws/session"]
        REST[REST APIs]
        Auth[JWT Auth Layer]
        Rate[Rate Limiter]
    end

    subgraph Pipeline["🔧 Processing Pipeline (Orchestrator)"]
        SEP["Demucs\nSource Separator"]
        STT["Whisper\nSpeech-to-Text"]
        CHORD["Madmom\nChord Detector"]
        NOTE["Librosa\nNote Analyzer"]
        STRUM["Librosa\nStrum Analyzer"]
        LLM["LM Studio\nLocal LLM"]
        TTS["Piper TTS\nVoice Synth"]
    end

    subgraph Storage["🗄️ Data Layer"]
        DB[(SQLite DB)]
        FS["File System\nTemp Audio"]
    end

    Mic -->|Raw Audio Bytes| WS
    Audio -->|Multipart Upload| REST
    UI -->|Text Messages| WS
    WS --> Auth
    REST --> Auth
    Auth --> Rate
    Rate --> Pipeline
    SEP -->|Guitar Stem| STT
    SEP -->|Guitar Stem| CHORD
    SEP -->|Guitar Stem| NOTE
    SEP -->|Guitar Stem| STRUM
    STT -->|Transcript| LLM
    CHORD -->|Chord Data| LLM
    NOTE -->|Note Data| LLM
    STRUM -->|Strum Data| LLM
    LLM -->|AI Response| TTS
    TTS -->|WAV Audio| WS
    Auth --> DB
    Pipeline --> FS

    style Client fill:#1a1a2e,stroke:#61DAFB,color:#fff
    style Gateway fill:#16213e,stroke:#009688,color:#fff
    style Pipeline fill:#0f3460,stroke:#e94560,color:#fff
    style Storage fill:#1a1a2e,stroke:#f5a623,color:#fff
```

### 🔄 Real-Time WebSocket Flow

```mermaid
sequenceDiagram
    participant U as 🎸 User
    participant FE as React UI
    participant WS as WebSocket
    participant ORCH as Orchestrator
    participant AI as AI Pipeline

    U->>FE: Record audio / type question
    FE->>WS: Connect with JWT token
    WS->>WS: Authenticate user
    FE->>WS: Binary audio chunks
    FE->>WS: stop_recording event
    WS->>ORCH: run_pipeline(audio, user_id, session_id)
    ORCH->>AI: Demucs + Whisper + Chord + Note + Strum
    AI-->>WS: status updates (real-time)
    WS-->>FE: {"type":"status","stage":"separating"}
    AI-->>ORCH: All results assembled
    ORCH-->>WS: transcription + chords + notes + LLM + TTS audio
    WS-->>FE: {"type":"chords","data":[...]}
    WS-->>FE: {"type":"response","text":"..."}
    WS-->>FE: {"type":"audio","format":"wav","data":"base64"}
    WS-->>FE: {"type":"complete"}
    FE->>U: Display results + play voice response
```

---

## 📁 Project Structure

```
guitar-tutor/
│
├── 📂 backend/                          # FastAPI Gateway (main entry point)
│   ├── 🐍 main.py                       # App setup, routes, WebSocket handler
│   ├── 🐍 orchestrator.py               # Full AI pipeline coordinator
│   ├── 🐍 config.py                     # All paths, model configs, constants
│   ├── 📂 auth/                         # JWT authentication
│   │   ├── router.py                    # /auth/signup, /login, /token, /me
│   │   ├── dependencies.py              # OAuth2 token validators
│   │   └── security.py                  # bcrypt + JWT helpers
│   ├── 📂 database/                     # SQLAlchemy ORM
│   │   ├── engine.py                    # SQLite async engine + init_db()
│   │   └── models.py                    # User, Session, Message, UserMemory
│   ├── 📂 routers/                      # API route modules
│   │   ├── sessions.py                  # CRUD for chat sessions
│   │   └── users.py                     # User profile endpoints
│   ├── 📂 schemas/                      # Pydantic request/response models
│   ├── 📂 services/                     # Business logic wrappers
│   │   ├── separator.py                 # Calls Demucs worker
│   │   ├── transcriber.py               # Calls Whisper worker
│   │   ├── chord_detector.py            # Calls Madmom worker
│   │   ├── note_analyzer.py             # Calls Librosa worker
│   │   └── llm_client.py                # LM Studio HTTP client
│   ├── 📂 workers/                      # Isolated subprocess scripts
│   │   ├── separate_worker.py           # Demucs (runs in own venv)
│   │   ├── transcribe_worker.py         # Whisper (runs in own venv)
│   │   ├── chord_worker.py              # Madmom (runs in own venv)
│   │   ├── note_worker.py               # Librosa (runs in own venv)
│   │   └── tts_worker.py                # Piper TTS
│   ├── 📂 middleware/                   # Rate limiting
│   └── 📄 requirements.txt
│
├── 📂 Instrument_Tutor_React_UI/        # React + TypeScript Frontend
│   ├── 📂 src/
│   │   ├── 📂 components/               # UI components (shadcn/ui)
│   │   ├── 📂 pages/                    # Route pages
│   │   ├── 📂 hooks/                    # Custom React hooks
│   │   ├── 📂 lib/                      # API clients, utilities
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── 📂 Instrument_Tutor_Backend/         # AI Model Venvs (isolated)
    ├── 📂 backend/venv/                 # Gateway dependencies
    ├── 📂 demucs-separator/venv/        # Demucs + PyTorch
    ├── 📂 whisper-piper/venv/           # OpenAI Whisper
    ├── 📂 madmom-chords/venv/           # Madmom chord ML
    └── 📂 librosa-analysis/venv/        # Librosa + NumPy
```

---

## 🛠️ Tech Stack

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat) React | 18+ | UI framework |
| ![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?logo=typescript&logoColor=white&style=flat) TypeScript | 5.0 | Type-safe development |
| ![Vite](https://img.shields.io/badge/-Vite-646CFF?logo=vite&logoColor=white&style=flat) Vite | 5.0 | Ultra-fast dev server & bundler |
| ![Tailwind](https://img.shields.io/badge/-Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white&style=flat) Tailwind CSS | 3.0 | Utility-first styling |
| shadcn/ui + Radix UI | — | Accessible component library |
| Framer Motion | 11+ | Smooth animations & transitions |

### Backend

| Technology | Version | Purpose |
|---|---|---|
| ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white&style=flat) FastAPI | 0.139 | Async REST + WebSocket gateway |
| ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat) Python | 3.12 | Backend runtime |
| SQLAlchemy | 2.0 | Async ORM (aiosqlite / MySQL) |
| Uvicorn | 0.51 | ASGI server with hot-reload |
| python-jose | 3.5 | JWT token signing & validation |
| bcrypt | 5.0 | Secure password hashing |

### AI / Machine Learning

| Model / Library | Purpose |
|---|---|
| 🔊 **OpenAI Whisper** (`base`) | Speech-to-text transcription |
| 🎵 **Demucs** (`htdemucs`) | Neural source separation — isolates guitar stem |
| 🎸 **Madmom** | Deep-learning chord recognition |
| 📊 **Librosa** | Note detection, pitch analysis, strumming patterns |
| 🤖 **LM Studio** | Local LLM inference (Mistral, Llama 3, etc.) |
| 🗣️ **Piper TTS** | Fast, offline neural text-to-speech |

---

## 🚀 Installation

> [!IMPORTANT]
> This project uses **multiple isolated Python virtual environments** — one per AI model — to avoid dependency conflicts between Demucs, Whisper, Madmom, and Librosa. Follow each step carefully.

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 – 3.12 |
| Node.js | 18+ |
| npm | 9+ |
| ffmpeg | Latest |
| LM Studio | Latest |

```bash
# macOS
brew install ffmpeg python@3.12 node

# Ubuntu / Debian
sudo apt install ffmpeg python3.12 nodejs npm

# Windows
winget install Gyan.FFmpeg Python.Python.3.12 OpenJS.NodeJS
```

---

## ⚙️ Backend Setup

<details>
<summary><b>📦 Step 1 — Clone & Setup Main Backend</b></summary>

```bash
git clone https://github.com/yourusername/guitar-tutor.git
cd guitar-tutor

cd Instrument_Tutor_Backend/backend
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

pip install -r ../../backend/requirements.txt
```

</details>

<details>
<summary><b>🎵 Step 2 — Setup Demucs (Source Separation)</b></summary>

```bash
cd guitar-tutor/Instrument_Tutor_Backend/demucs-separator
python3 -m venv venv
source venv/bin/activate
pip install demucs torch torchaudio
```

</details>

<details>
<summary><b>🗣️ Step 3 — Setup Whisper (Speech-to-Text)</b></summary>

```bash
cd guitar-tutor/Instrument_Tutor_Backend/whisper-piper
python3 -m venv venv
source venv/bin/activate
pip install openai-whisper
```

</details>

<details>
<summary><b>🎸 Step 4 — Setup Madmom (Chord Detection)</b></summary>

```bash
cd guitar-tutor/Instrument_Tutor_Backend/madmom-chords
python3 -m venv venv
source venv/bin/activate
pip install madmom
```

</details>

<details>
<summary><b>📊 Step 5 — Setup Librosa (Note & Strum Analysis)</b></summary>

```bash
cd guitar-tutor/Instrument_Tutor_Backend/librosa-analysis
python3 -m venv venv
source venv/bin/activate
pip install librosa numpy soundfile
```

</details>

<details>
<summary><b>🤖 Step 6 — Setup LM Studio (Local LLM)</b></summary>

1. Download [LM Studio](https://lmstudio.ai/) for your platform
2. Load a model (recommended: **Mistral 7B** or **Llama 3.1 8B**)
3. Go to the **Local Server** tab → click **Start Server**
4. Default URL: `http://localhost:1234/v1/chat/completions`

</details>

<details>
<summary><b>🔊 Step 7 — Setup Piper TTS (Optional Voice Responses)</b></summary>

```bash
# Download Piper binary: https://github.com/rhasspy/piper/releases
# Place binary at: guitar-tutor/whisper-piper/piper/piper

# Download a voice model: https://huggingface.co/rhasspy/piper-voices
# Place at: guitar-tutor/whisper-piper/piper/voices/en_US-amy-low.onnx
```

</details>

---

## 🖥️ Frontend Setup

```bash
cd guitar-tutor/Instrument_Tutor_React_UI
npm install
npm run dev
```

> The React app will be available at **http://localhost:5173**

---

## 🌍 Environment Variables

Create a `.env` file inside `backend/`:

```env
# ── Database ─────────────────────────────────────────
# Default: SQLite (auto-created, zero config)
# DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/guitar_tutor

# ── Authentication ───────────────────────────────────
SECRET_KEY=your_super_secret_jwt_key_change_in_production
ACCESS_TOKEN_EXPIRE_DAYS=7

# ── LM Studio ────────────────────────────────────────
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_TIMEOUT=30

# ── Whisper ──────────────────────────────────────────
WHISPER_MODEL=base   # tiny | base | small | medium | large

# ── Server ───────────────────────────────────────────
HOST=0.0.0.0
PORT=8000
```

> [!WARNING]
> Never commit your `.env` file. It is already listed in `.gitignore`.

---

## ▶️ Running the Project

### 1 · Start the Backend

```bash
cd guitar-tutor/backend
source ../Instrument_Tutor_Backend/backend/venv/bin/activate
python main.py
# or: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2 · Start the Frontend

```bash
cd guitar-tutor/Instrument_Tutor_React_UI
npm run dev
```

### 3 · Start LM Studio

Open LM Studio → load a model → click **Start Server**.

### ✅ Verify Everything is Running

| Service | URL | Expected |
|---|---|---|
| Backend API | http://localhost:8000 | FastAPI running |
| Swagger Docs | http://localhost:8000/docs | Interactive API docs |
| Frontend | http://localhost:5173 | React app |
| LM Studio | http://localhost:1234 | LLM server |
| WebSocket | ws://localhost:8000/ws/session | Real-time session |

---

## 📖 API Documentation

Interactive Swagger UI is auto-generated at: **http://localhost:8000/docs**

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/signup` | Register a new user (JSON body) |
| `POST` | `/auth/login` | Login — returns JWT (JSON body) |
| `POST` | `/auth/token` | OAuth2 form login (Swagger Authorize button) |
| `GET` | `/auth/me` | Get current authenticated user |

### Audio Pipeline

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/pipeline` | Full pipeline: audio → all AI → TTS |
| `POST` | `/api/separate` | Separate audio stems with Demucs |
| `POST` | `/api/transcribe` | Transcribe audio with Whisper |
| `POST` | `/api/chords` | Detect chords with Madmom |
| `POST` | `/api/ask` | Text-only LLM query |
| `POST` | `/api/tts` | Text-to-speech with Piper |

### Session Management

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/sessions` | List all user sessions |
| `POST` | `/api/sessions` | Create a new session |
| `GET` | `/api/sessions/{id}` | Get session with all messages |
| `PUT` | `/api/sessions/{id}` | Update session title |
| `DELETE` | `/api/sessions/{id}` | Delete a session |

### WebSocket Protocol

```
ws://localhost:8000/ws/session?token=<JWT>&session_id=<UUID>
```

**Client → Server messages:**

```json
{ "type": "start_recording" }
{ "type": "stop_recording" }
{ "type": "text_input", "text": "What is a G chord?" }
```

**Server → Client messages:**

```json
{ "type": "status",       "stage": "separating", "message": "Isolating guitar..." }
{ "type": "transcription","text": "Am I playing E minor correctly?" }
{ "type": "chords",       "data": [...], "unique_chords": ["E:min", "D:maj"] }
{ "type": "notes",        "data": [...] }
{ "type": "strumming",    "data": { "bpm": 83, "pattern": "D-U-D-U", "stability": 0.94 } }
{ "type": "response",     "text": "Great job! Your E minor shape is clean..." }
{ "type": "audio",        "format": "wav", "data": "<base64_encoded_wav>" }
{ "type": "complete",     "total_time": 4.2, "stages_completed": ["separate","transcribe","chords","llm","tts"] }
```

---

## 🖼️ Screenshots

<div align="center">

### 🏠 Landing Page
<img src="docs/screenshots/landing.png" alt="Landing Page" width="90%"/>

*Glassmorphism hero with ambient gradients and animated CTA*

---

### 🔐 Authentication
<img src="docs/screenshots/auth.png" alt="Authentication Modal" width="70%"/>

*Elegant sign in / sign up modal with dark glassmorphism theme*

---

### 💬 AI Chat Interface
<img src="docs/screenshots/chat_overview.png" alt="AI Guitar Tutor Chat" width="90%"/>

*Real-time conversation with the AI guitar tutor*

---

### 🥁 Strumming Pattern Analysis
<img src="docs/screenshots/strumming.png" alt="Strumming Analysis" width="90%"/>

*83 BPM · 27 strums · 94% stable — visual D/U stroke breakdown*

---

### 🎵 Song & Chord Guidance
<img src="docs/screenshots/song_guidance.png" alt="AI Song Guidance" width="90%"/>

*AI identifies which songs use your detected chords and explains technique*

</div>

> 📸 Place your screenshots in `docs/screenshots/` with these filenames:
> `landing.png`, `auth.png`, `chat_overview.png`, `strumming.png`, `song_guidance.png`

---

## 🔮 Future Enhancements

| Feature | Status | Priority |
|---|---|---|
| 🎹 Piano / Bass guitar support | Planned | High |
| 📱 Mobile app (React Native) | Planned | High |
| 🌐 Streaming LLM responses (token-by-token) | In Progress | High |
| 🎼 Sheet music / guitar tab generation | Planned | Medium |
| 👥 Multi-user collaborative sessions | Planned | Medium |
| 📈 Progress tracking & analytics dashboard | Planned | Medium |
| 🎤 Singing pitch correction feedback | Planned | Low |
| 🌍 Multi-language tutor support | Planned | Low |
| ☁️ Docker + Cloud deployment (AWS/GCP) | Planned | High |
| 🔌 DAW plugin (VST/AU) integration | Research | Low |

---

## ⚡ Performance Highlights

```
┌─────────────────────────────────────────────────────────────────┐
│                    Pipeline Performance                         │
├─────────────────────────┬──────────────────────────────────────┤
│  Stage                  │  Typical Time                        │
├─────────────────────────┼──────────────────────────────────────┤
│  Audio Upload           │  < 200ms                             │
│  Demucs Separation      │  2–8s (GPU) / 15–30s (CPU)          │
│  Whisper Transcription  │  1–3s (base model)                   │
│  Chord Detection        │  1–2s                                │
│  Note Analysis          │  0.5–1s                              │
│  LLM Inference          │  2–5s (7B model, CPU)                │
│  Piper TTS              │  < 1s                                │
├─────────────────────────┼──────────────────────────────────────┤
│  Total (end-to-end)     │  ~7–15s typical                      │
└─────────────────────────┴──────────────────────────────────────┘
```

> [!TIP]
> Use a **GPU** for Demucs and Whisper to dramatically cut pipeline time. With an NVIDIA GPU, end-to-end latency drops to **3–5 seconds**.

---

## 🤝 Contributing

Contributions are warmly welcomed!

```bash
# 1. Fork this repository
# 2. Clone your fork
git clone https://github.com/yourusername/guitar-tutor.git

# 3. Create a feature branch
git checkout -b feature/my-new-feature

# 4. Commit your changes
git commit -m "feat: add my new feature"

# 5. Push and open a Pull Request
git push origin feature/my-new-feature
```

**Guidelines:**
- ✅ Follow existing code style and naming conventions
- ✅ Add docstrings to new Python functions
- ✅ Write meaningful commit messages (Conventional Commits preferred)
- ✅ Update the README if you add new features or configuration
- ❌ Never commit `.env` files, API keys, or credentials

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License — Copyright (c) 2026 Ashutosh Kale

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
```

---

## 👨‍💻 Author

<div align="center">

<img src="https://github.com/ashutoshkale18.png" width="100" height="100" style="border-radius:50%" alt="Ashutosh Kale"/>

### **Ashutosh Kale**
*Full Stack Developer · AI/ML Enthusiast · Musician*

[![GitHub](https://img.shields.io/badge/GitHub-ashutoshkale18-181717?style=for-the-badge&logo=github)](https://github.com/ashutoshkale18)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/ashutoshkale)

</div>

---

## 🙏 Acknowledgements

| Project | Contribution |
|---|---|
| [OpenAI Whisper](https://github.com/openai/whisper) | State-of-the-art open-source speech recognition |
| [Demucs](https://github.com/facebookresearch/demucs) | Neural music source separation by Meta AI Research |
| [Madmom](https://github.com/CPJKU/madmom) | Deep learning audio and music analysis |
| [Librosa](https://librosa.org/) | Python library for audio and music analysis |
| [Piper TTS](https://github.com/rhasspy/piper) | Fast, local, offline neural text-to-speech |
| [LM Studio](https://lmstudio.ai/) | Run LLMs locally with a beautiful UI |
| [FastAPI](https://fastapi.tiangolo.com/) | Modern, high-performance Python web framework |
| [shadcn/ui](https://ui.shadcn.com/) | Beautiful, accessible React component library |
| [Framer Motion](https://www.framer.com/motion/) | Production-ready React animation library |

---

<div align="center">

**⭐ If this project helped or inspired you, please give it a star on GitHub!**

Made with ❤️ and 🎸 by [Ashutosh Kale](https://github.com/ashutoshkale18)

*"Music is the shorthand of emotion."* — Leo Tolstoy

</div>
