import React, { useState, useEffect, useRef } from 'react';
import { Mic, Send, Play, Square } from 'lucide-react';

const formatChordName = (chord) => {
  return chord
    .replace(":maj", " Maj")
    .replace(":min", " Min")
    .replace(":7", "7")
    .replace(":min7", "m7")
    .replace(":maj7", "M7");
};

const getChordColor = (chord) => {
  if (chord === "N") return "var(--chord-none)";
  if (chord.includes("min")) return "var(--chord-minor)";
  if (chord.includes("maj")) return "var(--chord-major)";
  return "var(--chord-other)";
};

const getChordClass = (chord) => {
  if (chord.includes("min")) return "minor";
  if (chord.includes("maj")) return "major";
  return "other";
};

const AudioPlayer = ({ base64 }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    if (base64) {
      const audioData = atob(base64);
      const arrayBuffer = new ArrayBuffer(audioData.length);
      const view = new Uint8Array(arrayBuffer);
      for (let i = 0; i < audioData.length; i++) {
        view[i] = audioData.charCodeAt(i);
      }
      const blob = new Blob([arrayBuffer], { type: "audio/wav" });
      const url = URL.createObjectURL(blob);
      audioRef.current = new Audio(url);
      
      audioRef.current.onended = () => setIsPlaying(false);

      return () => {
        URL.revokeObjectURL(url);
        if (audioRef.current) audioRef.current.pause();
      };
    }
  }, [base64]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  if (!base64) return null;

  return (
    <div className="audio-player-mini">
      <button onClick={togglePlay}>
        {isPlaying ? <Square size={16} fill="currentColor" /> : <Play size={16} fill="currentColor" />}
      </button>
      <div className="audio-wave-mini">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="bar" style={{ height: isPlaying ? `${Math.random() * 16 + 4}px` : '4px' }} />
        ))}
      </div>
    </div>
  );
};

const TutorInterface = ({ tutor }) => {
  const [text, setText] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [tutor.messages, tutor.pipelineStage]);

  const handleSend = () => {
    if (text.trim()) {
      tutor.sendTextMessage(text);
      setText("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const stageOrder = ["separating", "transcribing", "analyzing", "thinking", "speaking", "complete"];
  const currentIdx = stageOrder.indexOf(tutor.pipelineStage === "processing" ? "transcribing" : tutor.pipelineStage);

  return (
    <div className="chat-overlay">
      <div className="messages-container">
        <div style={{ flex: 1, minHeight: '50px' }}></div>
        {tutor.messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="message-bubble">
              {msg.text}
              
              {/* Audio Playback */}
              {msg.audioBase64 && <AudioPlayer base64={msg.audioBase64} />}

              {/* Chord Chips */}
              {msg.uniqueChords && msg.uniqueChords.length > 0 && (
                <div className="chord-chips">
                  {msg.uniqueChords.filter(c => c !== "N").map((c, i) => (
                    <span key={i} className={`chord-chip ${getChordClass(c)}`}>
                      {formatChordName(c)}
                    </span>
                  ))}
                </div>
              )}

              {/* Chord Timeline */}
              {msg.chords && msg.chords.length > 0 && (
                <div className="chord-timeline">
                  {(() => {
                    const totalDuration = msg.chords[msg.chords.length - 1].end - msg.chords[0].start;
                    return msg.chords.map((chordObj, i) => {
                      const duration = chordObj.end - chordObj.start;
                      const pct = (duration / totalDuration) * 100;
                      return (
                        <div 
                          key={i} 
                          className="chord-segment"
                          style={{ width: `${pct}%`, backgroundColor: getChordColor(chordObj.chord) }}
                          title={`${formatChordName(chordObj.chord)}`}
                        >
                          {chordObj.chord === "N" ? "" : formatChordName(chordObj.chord)}
                        </div>
                      );
                    });
                  })()}
                </div>
              )}
            </div>
          </div>
        ))}

        {tutor.pipelineStage !== "complete" && (
          <div className="message assistant">
            <div className="message-bubble" style={{ display: 'flex', gap: '4px' }}>
              <span style={{ animation: 'float 1s infinite alternate' }}>•</span>
              <span style={{ animation: 'float 1s infinite alternate 0.2s' }}>•</span>
              <span style={{ animation: 'float 1s infinite alternate 0.4s' }}>•</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="control-bar">
        {/* Pipeline Status */}
        {tutor.pipelineStage !== "complete" && (
          <div className="pipeline-status">
            {stageOrder.slice(0, 5).map((stage, idx) => (
              <React.Fragment key={stage}>
                <span className={`pipeline-step ${idx < currentIdx ? 'done' : idx === currentIdx ? 'active' : ''}`}>
                  {stage.charAt(0).toUpperCase() + stage.slice(1)}
                </span>
                {idx < 4 && <span style={{ opacity: 0.3 }}>/</span>}
              </React.Fragment>
            ))}
          </div>
        )}

        <div className="input-row">
          <input 
            type="text" 
            className="text-input" 
            placeholder="Ask about guitar, chords, techniques..." 
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button 
            className={`mic-btn ${tutor.isRecording ? 'recording' : ''}`}
            onClick={tutor.toggleRecording}
          >
            {tutor.isRecording ? <Square size={20} fill="currentColor" /> : <Mic size={24} />}
          </button>
          <button className="mic-btn" style={{ background: 'rgba(255,255,255,0.1)' }} onClick={handleSend}>
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default TutorInterface;
