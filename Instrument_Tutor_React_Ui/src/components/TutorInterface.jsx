import React, { useState, useEffect, useRef } from 'react';
import { Mic, Send, Play, Square, Music, Activity } from 'lucide-react';

const formatChordName = (chord) => {
  return chord
    .replace(":maj", " Maj")
    .replace(":min", " Min")
    .replace(":7", "7")
    .replace(":min7", "m7")
    .replace(":maj7", "M7");
};

const getChordColor = (chord) => {
  if (chord === "N") return "transparent";
  if (chord.includes("min")) return "var(--chord-minor, #9b72cb)";
  if (chord.includes("maj")) return "var(--chord-major, #3b6ef0)";
  return "var(--chord-other, #e08a3c)";
};

const AudioPlayer = ({ base64, audioUrl }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    if (audioUrl) {
      audioRef.current = new Audio(audioUrl);
      audioRef.current.onended = () => setIsPlaying(false);
      return () => {
        if (audioRef.current) audioRef.current.pause();
      };
    } else if (base64 && base64 !== "NOT_LOADED") {
      try {
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
      } catch (err) {
        console.error("Failed to decode audio base64", err);
      }
    }
  }, [base64, audioUrl]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => {
        setIsPlaying(true);
      }).catch(err => {
        console.error("Audio play failed:", err);
        setIsPlaying(false);
      });
    }
  };

  if (!base64 && !audioUrl) return null;

  return (
    <div className="guitar-audio-player">
      <button onClick={togglePlay} style={{background: 'none', border: 'none', color: '#fff', cursor: 'pointer', padding: 0}}>
        {isPlaying ? <Square size={14} fill="currentColor" /> : <Play size={14} fill="currentColor" />}
      </button>
      <div style={{display: 'flex', alignItems: 'flex-end', gap: '2px', height: '16px'}}>
        {[...Array(20)].map((_, i) => (
          <div 
            key={i} 
            style={{ width: '3px', borderRadius: '99px', background: 'rgba(95, 124, 232, 0.8)', transition: 'all 0.07s', height: isPlaying ? `${Math.random() * 12 + 4}px` : '4px' }} 
          />
        ))}
      </div>
    </div>
  );
};

const TutorInterface = ({ tutor, toggleSidebar, isSidebarOpen }) => {
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

  const isProcessing = tutor.pipelineStage !== "complete" && tutor.pipelineStage !== "idle";

  return (
    <div className="main">
      
      <div className="topbar">
        <div className="topbar-left">
          <button onClick={toggleSidebar} style={{background: 'none', border: 'none', color: '#fff', cursor: 'pointer', padding: '8px', marginRight: '4px'}}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
          </button>
          <h1>AI Guitar Tutor</h1>
          <span className="plus-badge">Plus</span>
        </div>
      </div>

      <div className="content">
        
        {tutor.messages.length === 0 && (
          <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', maxWidth: '780px', marginTop: '20px'}}>
            <div className="greet-avatar"></div>
            <div className="greet-title">Hi, there 👋</div>
            <div className="greet-sub">Tell us what you want to learn, and we'll handle the rest.</div>
            
            <div className="pills-row">
              <div className="pill" onClick={() => tutor.sendTextMessage("How do I play a G Major chord?")}>
                <span className="ic-circle" style={{background: 'rgba(59,110,240,0.2)', color: '#5f7ce8'}}>
                  <Music size={14} />
                </span>
                How to play G Major?
              </div>
              <div className="pill" onClick={() => tutor.sendTextMessage("Can you analyze my strumming rhythm?")}>
                <span className="ic-circle" style={{background: 'rgba(224,96,138,0.2)', color: '#e0608a'}}>
                  <Activity size={14} />
                </span>
                Analyze my strumming
              </div>
              <div className="pill" onClick={() => tutor.sendTextMessage("What is a 12-bar blues progression?")}>
                <span className="ic-circle" style={{background: 'rgba(224,138,60,0.2)', color: '#e08a3c'}}>
                  <Music size={14} />
                </span>
                12-bar blues?
              </div>
            </div>
          </div>
        )}

        <div className="chat-messages">
          {tutor.messages.map((msg) => (
            <React.Fragment key={msg.id}>
              {msg.role === 'assistant' ? (
                <div className="card dark">
                  <div className="card-dark-head">
                    <div className="card-dark-avatar">AI</div>
                    <span className="name">Guitar Tutor</span>
                  </div>
                  <div className="card-dark-desc">
                    {msg.text}
                  </div>
                  
                  {(msg.audioBase64 || msg.audioUrl) && <AudioPlayer base64={msg.audioBase64} audioUrl={msg.audioUrl} />}

                  {msg.uniqueChords && msg.uniqueChords.length > 0 && (
                    <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px'}}>
                      {msg.uniqueChords.filter(c => c !== "N").map((c, i) => (
                        <span key={i} className="guitar-chord-chip">
                          {formatChordName(c)}
                        </span>
                      ))}
                    </div>
                  )}

                  {msg.chords && msg.chords.length > 0 && (
                    <div style={{marginTop: '12px', background: 'rgba(0,0,0,0.4)', borderRadius: '8px', overflow: 'hidden', display: 'flex', height: '24px', width: '100%', border: '1px solid rgba(255,255,255,0.1)'}}>
                      {(() => {
                        const totalDuration = msg.chords[msg.chords.length - 1].end - msg.chords[0].start;
                        return msg.chords.map((chordObj, i) => {
                          const duration = chordObj.end - chordObj.start;
                          const pct = (duration / totalDuration) * 100;
                          if (chordObj.chord === "N") return <div key={i} style={{ width: `${pct}%`, background: 'transparent' }} />;
                          return (
                            <div 
                              key={i} 
                              style={{ width: `${pct}%`, backgroundColor: getChordColor(chordObj.chord), height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 'bold', color: '#fff', overflow: 'hidden', borderRight: '1px solid rgba(0,0,0,0.2)' }}
                              title={`${formatChordName(chordObj.chord)}`}
                            >
                              {pct > 5 ? formatChordName(chordObj.chord) : ''}
                            </div>
                          );
                        });
                      })()}
                    </div>
                  )}

                  {msg.strumming && (
                    <div style={{marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.1)'}}>
                      <div style={{display: 'flex', gap: '16px', flexWrap: 'wrap', fontSize: '12px', color: '#a9aab0', fontWeight: 500}}>
                        {msg.strumming.tempo_bpm > 0 && <span style={{display: 'flex', alignItems: 'center', gap: '6px'}}><Activity size={12}/> {Math.round(msg.strumming.tempo_bpm)} BPM</span>}
                        {msg.strumming.total_strums > 0 && <span>✋ {msg.strumming.total_strums} strums</span>}
                        {msg.strumming.tempo_stability !== undefined && (
                          <span>📊 {Math.round(msg.strumming.tempo_stability * 100)}% stable</span>
                        )}
                      </div>
                      {msg.strumming.pattern && (
                        <div style={{display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '10px'}}>
                          {msg.strumming.pattern.split("-").map((dir, i) => (
                            <span key={i} style={{padding: '2px 8px', borderRadius: '5px', fontSize: '10px', fontWeight: 'bold', background: dir === "D" ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.05)', color: dir === "D" ? '#fff' : '#9a9aa3', border: dir === "D" ? '1px solid rgba(255,255,255,0.2)' : '1px solid rgba(255,255,255,0.1)'}}>
                              {dir === "D" ? "↓ D" : "↑ U"}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="user-msg">
                  {msg.text}
                  {msg.audioUrl && (
                    <div style={{marginTop: '8px', fontSize: '11px', color: '#9db6f7', display: 'flex', alignItems: 'center', gap: '4px', opacity: 0.7}}>
                      <Mic size={10} /> Audio attached
                    </div>
                  )}
                </div>
              )}
            </React.Fragment>
          ))}

          {isProcessing && (
            <div className="card dark" style={{background: 'transparent', border: 'none', padding: '10px 20px'}}>
               <div style={{display: 'flex', alignItems: 'center', gap: '12px', color: '#a6a6ad'}}>
                 <div style={{display: 'flex', gap: '4px'}}>
                   <span style={{width: '6px', height: '6px', background: '#a6a6ad', borderRadius: '50%', animation: 'float 1s infinite'}} />
                   <span style={{width: '6px', height: '6px', background: '#a6a6ad', borderRadius: '50%', animation: 'float 1s infinite 0.2s'}} />
                   <span style={{width: '6px', height: '6px', background: '#a6a6ad', borderRadius: '50%', animation: 'float 1s infinite 0.4s'}} />
                 </div>
                 <span style={{fontSize: '12px', fontWeight: 500, textTransform: 'capitalize'}}>{tutor.pipelineStage}...</span>
               </div>
            </div>
          )}
          
          <div ref={messagesEndRef} style={{height: '20px'}} />
        </div>
      </div>

      <div className="input-area">
        <div className="input-box">
          <div className="input-top">
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M7.5 1l1 3 3 1-3 1-1 3-1-3-3-1 3-1 1-3z" stroke="currentColor" strokeWidth="1" strokeLinejoin="round"/></svg>
            <input 
              type="text" 
              placeholder="Ask about guitar, chords, techniques..." 
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
            />
          </div>
          
          <div className="input-bottom">
            <div style={{display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', fontWeight: 500, color: '#7a7a82'}}>
               {isProcessing ? (
                 <span style={{display: 'flex', alignItems: 'center', gap: '8px', color: '#5f7ce8'}}>
                    <Activity size={12} />
                    Processing audio...
                 </span>
               ) : (
                 <span style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                    <Music size={12} />
                    Ready
                 </span>
               )}
            </div>

            <div className="input-actions">
              <button 
                onClick={tutor.toggleRecording}
                className={`ia-btn ${tutor.isRecording ? 'recording' : ''}`}
                title={tutor.isRecording ? "Stop recording" : "Record audio"}
              >
                {tutor.isRecording ? <Square size={14} fill="currentColor" /> : <Mic size={16} />}
              </button>
              <button 
                onClick={handleSend}
                disabled={!text.trim() && !tutor.isRecording}
                className="send-btn"
              >
                Send
                <Send size={12} />
              </button>
            </div>
          </div>
        </div>
        <div className="footnote">
          AI Tutor may display inaccurate info, so please double check the response.
        </div>
      </div>
      
    </div>
  );
};

export default TutorInterface;
