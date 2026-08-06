<div align="center">

# 🎸 Guitar Tutor AI — React Frontend

### *Interactive Voice & AI-Powered Guitar Learning Dashboard*

[![React](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/JavaScript%2FJSX-ES6%2B-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Vite](https://img.shields.io/badge/Vite-8.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<br/>

**The modern, animated web interface for Guitar Tutor AI — featuring real-time audio visualization, glassmorphism dark theme, interactive chord & strum analysis, and voice interaction.**

[🚀 Installation Guide](#-installation-guide) · [⚙️ Configuration](#%EF%B8%8F-configuration) · [📜 Available Scripts](#-available-scripts) · [📁 Project Structure](#-project-structure)

</div>

---

## 🌟 Overview

This directory contains the **React 19 + Vite** web client for **Guitar Tutor AI**. It connects seamlessly to the FastAPI gateway backend over REST APIs and WebSockets to provide:

- 🎙️ **Real-time Voice & Audio Recording** with microphone waveform controls
- 🎸 **Interactive Chord & Strum Analysis Display** (BPM, stability %, D/U stroke patterns)
- 🤖 **AI Assistant Chat Interface** powered by local LLM feedback & Piper TTS voice output
- 🔐 **JWT User Authentication** (Sign up / Sign in modals & session management)
- 🎨 **Sleek Glassmorphism Dark UI** built with Tailwind CSS v4, Framer Motion, and Lucide React icons

---

## 🛠️ Tech Stack

| Library / Tool | Version | Purpose |
|---|---|---|
| **React** | `^19.2.6` | Component-based UI library |
| **Vite** | `^8.0.16` | Next-generation frontend tooling & dev server |
| **Tailwind CSS** | `^4.3.1` | Utility-first CSS framework |
| **Framer Motion** | `^12.40.0` | Fluid animations & micro-interactions |
| **Lucide React** | `^1.21.0` | Modern, clean UI icon set |
| **Axios** | `^1.18.1` | Promise-based HTTP client for REST endpoints |
| **React Router** | `^7.18.0` | Single Page Application (SPA) routing |
| **Three.js / Fiber**| `^0.184.0` | 3D audio & canvas visuals |

---

## 📌 Prerequisites

Before running the frontend, ensure you have installed:

- **Node.js**: `v18.0.0` or higher (Recommended: Node 20 LTS or 22 LTS)
- **npm**: `v9.0.0` or higher (comes bundled with Node.js)
- **Guitar Tutor Backend**: Running at `http://localhost:8000` (FastAPI Gateway)

Check your Node and npm versions:
```bash
node -v
npm -v
```

---

## 🚀 Installation Guide

Follow these steps to get the React frontend running locally:

### Step 1: Navigate to the Frontend Directory

If you are at the root of the repository (`guitar-tutor`):

```bash
cd Instrument_Tutor_React_Ui
```

### Step 2: Install Node Dependencies

Install all required NPM packages:

```bash
npm install
```

> 💡 **Tip:** If you encounter peer dependency warnings on Node 20+, you can use `npm install --legacy-peer-deps`.

---

## ⚙️ Configuration

### Environment Setup (Optional)

By default, the application connects to the local FastAPI backend running at `http://localhost:8000` and WebSocket at `ws://localhost:8000/ws/session`.

If your backend is running on a custom host or port, create a `.env` file inside `Instrument_Tutor_React_Ui/`:

```env
# Backend REST API Base URL
VITE_API_BASE_URL=http://localhost:8000

# Backend WebSocket Endpoint
VITE_WS_URL=ws://localhost:8000/ws/session
```

---

## ▶️ Running the Application

### 1. Start Development Server

Run Vite dev server with hot-module replacement (HMR):

```bash
npm run dev
```

Output:
```text
  VITE v8.0.16  ready in 280 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

Open **http://localhost:5173** in your browser.

---

### 2. Build for Production

To create an optimized production build:

```bash
npm run build
```

This compiles output files into the `dist/` directory.

---

### 3. Preview Production Build

To test the built production files locally before deploying:

```bash
npm run preview
```

---

## 📜 Available Scripts

In the project directory, you can run:

| Command | Description |
|---|---|
| `npm run dev` | Starts local development server on `http://localhost:5173` |
| `npm run build` | Builds optimized application bundle for production in `dist/` |
| `npm run preview` | Locally previews production build |
| `npm run lint` | Runs ESLint to check for code quality and syntax issues |

---

## 📁 Project Structure

```
Instrument_Tutor_React_Ui/
├── 📂 public/                   # Static public assets
├── 📂 src/
│   ├── 📂 assets/               # Images, brand graphics, & audio samples
│   ├── 📂 components/           # Reusable UI components
│   │   ├── Sidebar.jsx          # Session history & user menu navigation
│   │   ├── ChatContainer.jsx    # Real-time voice & text chat view
│   │   ├── StrumCard.jsx        # Visual strumming pattern & BPM widget
│   │   ├── AudioPlayer.jsx      # Neural Piper TTS voice playback
│   │   └── AuthModal.jsx        # Login & Signup popup modals
│   ├── 📂 contexts/             # Global React Contexts
│   │   └── AuthContext.jsx      # JWT Auth state & login token handler
│   ├── 📂 hooks/                # Custom React hooks (audio recorder, websocket)
│   ├── 📂 pages/                # Main Application Views
│   │   ├── LandingPage.jsx      # Animated marketing & hero entrance page
│   │   └── Dashboard.jsx        # Core AI Tutor workspace
│   ├── App.jsx                  # Main application routes & layout
│   ├── main.jsx                 # Vite application entry point
│   └── index.css                # Tailwind CSS imports & global design tokens
├── package.json                 # Node dependencies & npm scripts
├── tailwind.config.js           # Tailwind design tokens & themes
└── vite.config.js               # Vite build configuration
```

---

## 🔌 Connecting to Backend

Make sure the FastAPI backend server is active before interacting with the chat or recording voice.

1. Start Backend: `python main.py` in `backend/` (runs on `http://localhost:8000`)
2. Start Frontend: `npm run dev` in `Instrument_Tutor_React_Ui/` (runs on `http://localhost:5173`)
3. Open `http://localhost:5173`, log in, and press the **Microphone** icon to begin practicing!

---

## 📄 License

This frontend is part of the **Guitar Tutor AI** project and is licensed under the [MIT License](https://opensource.org/licenses/MIT).

