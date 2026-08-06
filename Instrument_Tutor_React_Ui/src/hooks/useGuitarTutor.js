import { useState, useEffect, useRef, useCallback } from 'react';

const WS_URL = "ws://localhost:8000/ws/session";
const API_URL = "http://localhost:8000";

// Encode raw PCM Float32 samples into a WAV ArrayBuffer
function encodeWAV(samples, sampleRate) {
  const numSamples = samples.length;
  const buffer = new ArrayBuffer(44 + numSamples * 2);
  const view = new DataView(buffer);

  function writeString(dv, offset, string) {
    for (let i = 0; i < string.length; i++) {
      dv.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + numSamples * 2, true);
  writeString(view, 8, "WAVE");

  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);

  writeString(view, 36, "data");
  view.setUint32(40, numSamples * 2, true);

  let offset = 44;
  for (let i = 0; i < numSamples; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    offset += 2;
  }

  return buffer;
}

export function useGuitarTutor() {
  const [status, setStatus] = useState("disconnected");
  const [pipelineStage, setPipelineStage] = useState("complete");
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [uniqueChords, setUniqueChords] = useState([]);
  
  const wsRef = useRef(null);
  const recStateRef = useRef({
    audioContext: null,
    audioSource: null,
    audioProcessor: null,
    stream: null,
    pcmBuffers: [],
    active: false,
  });
  const pendingUserTextRef = useRef(null);

  const addMessage = useCallback((msg) => {
    setMessages(prev => [...prev, { id: Date.now() + Math.random(), ...msg }]);
  }, []);

  // Connect WebSocket
  useEffect(() => {
    let timeout;
    let cancelled = false;

    function handleServerMessage(msg) {
      switch (msg.type) {
        case "status":
          setPipelineStage(msg.stage);
          break;
        case "transcription":
          if (msg.text && msg.text !== pendingUserTextRef.current) {
            addMessage({ role: "user", text: msg.text });
          }
          pendingUserTextRef.current = null;
          break;
        case "chords":
          if (msg.data && msg.data.length > 0) {
            setUniqueChords(msg.unique_chords || []);
            addMessage({ 
              role: "assistant", 
              type: "chords", 
              text: "Detected chords:", 
              chords: msg.data,
              uniqueChords: msg.unique_chords 
            });
          }
          break;
        case "response":
          if (msg.text) addMessage({ role: "assistant", text: msg.text });
          setPipelineStage("complete");
          break;
        case "audio":
          if (msg.data) {
            setMessages(prev => {
              const copy = [...prev];
              if (copy.length > 0 && copy[copy.length - 1].role === "assistant") {
                copy[copy.length - 1] = { ...copy[copy.length - 1], audioBase64: msg.data };
              }
              return copy;
            });
          }
          break;
        case "complete":
          setPipelineStage("complete");
          pendingUserTextRef.current = null;
          break;
        case "error":
          setPipelineStage("complete");
          pendingUserTextRef.current = null;
          addMessage({ role: "assistant", text: `⚠️ ${msg.message}` });
          break;
        default:
          break;
      }
    }

    function connect() {
      if (cancelled) return;
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

      const ws = new WebSocket(WS_URL);
      ws.onopen = () => setStatus("connected");
      ws.onclose = () => {
        setStatus("disconnected");
        if (!cancelled) timeout = setTimeout(connect, 3000);
      };
      ws.onerror = () => setStatus("error");
      ws.onmessage = (event) => {
        try {
          handleServerMessage(JSON.parse(event.data));
        } catch (e) {
          console.error("Failed to parse message:", e);
        }
      };
      wsRef.current = ws;
    }

    connect();

    return () => {
      cancelled = true;
      clearTimeout(timeout);
      if (wsRef.current) wsRef.current.close();
    };
  }, [addMessage]);

  // --- Recording: click to start, click to stop ---
  const doStartRecording = useCallback(async () => {
    const rec = recStateRef.current;
    if (rec.active) return; // already recording

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
      });

      const ctx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      const source = ctx.createMediaStreamSource(stream);
      const processor = ctx.createScriptProcessor(4096, 1, 1);

      rec.audioContext = ctx;
      rec.audioSource = source;
      rec.audioProcessor = processor;
      rec.stream = stream;
      rec.pcmBuffers = [];
      rec.active = true;

      processor.onaudioprocess = (e) => {
        if (recStateRef.current.active) {
          const data = e.inputBuffer.getChannelData(0);
          recStateRef.current.pcmBuffers.push(new Float32Array(data));
        }
      };

      source.connect(processor);
      processor.connect(ctx.destination);

      setIsRecording(true);

      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "start_recording" }));
      }

      console.log("Recording started");
    } catch (err) {
      console.error("Mic error:", err);
      addMessage({ role: "assistant", text: "⚠️ Could not access microphone. Check browser permissions." });
    }
  }, [addMessage]);

  const doStopRecording = useCallback(() => {
    const rec = recStateRef.current;
    if (!rec.active) return;
    rec.active = false;
    setIsRecording(false);

    // Tear down audio nodes
    try { rec.audioProcessor?.disconnect(); } catch (e) { /* ignore */ }
    try { rec.audioSource?.disconnect(); } catch (e) { /* ignore */ }
    try { rec.stream?.getTracks().forEach(t => t.stop()); } catch (e) { /* ignore */ }
    try { rec.audioContext?.close(); } catch (e) { /* ignore */ }

    const buffers = rec.pcmBuffers;
    rec.pcmBuffers = [];
    rec.audioContext = null;
    rec.audioSource = null;
    rec.audioProcessor = null;
    rec.stream = null;

    if (buffers.length === 0) {
      console.warn("No audio captured");
      addMessage({ role: "assistant", text: "⚠️ No audio captured. Try clicking the mic, speaking, then clicking again." });
      return;
    }

    const totalLength = buffers.reduce((sum, buf) => sum + buf.length, 0);
    const combined = new Float32Array(totalLength);
    let offset = 0;
    for (const buf of buffers) {
      combined.set(buf, offset);
      offset += buf.length;
    }

    const durationSec = totalLength / 16000;
    console.log(`Audio captured: ${durationSec.toFixed(1)}s`);

    if (durationSec < 0.5) {
      addMessage({ role: "assistant", text: "⚠️ Recording too short. Hold for at least 1 second." });
      return;
    }

    const wavBuffer = encodeWAV(combined, 16000);

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(wavBuffer);
      wsRef.current.send(JSON.stringify({ type: "stop_recording" }));
      console.log("Audio sent to backend");
    } else {
      addMessage({ role: "assistant", text: "⚠️ Not connected to backend. Cannot send audio." });
    }
  }, [addMessage]);

  const toggleRecording = useCallback(() => {
    if (recStateRef.current.active) {
      doStopRecording();
    } else {
      doStartRecording();
    }
  }, [doStartRecording, doStopRecording]);

  const sendTextMessage = useCallback((text) => {
    addMessage({ role: "user", text });
    pendingUserTextRef.current = text;
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "text_input", text }));
    } else {
      fetch(`${API_URL}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      })
      .then(r => r.json())
      .then(data => {
        pendingUserTextRef.current = null;
        addMessage({ role: "assistant", text: data.response });
      })
      .catch(err => {
        pendingUserTextRef.current = null;
        addMessage({ role: "assistant", text: `⚠️ Error: ${err.message}` });
      });
    }
  }, [addMessage]);

  return {
    status,
    pipelineStage,
    messages,
    isRecording,
    uniqueChords,
    toggleRecording,
    sendTextMessage
  };
}
