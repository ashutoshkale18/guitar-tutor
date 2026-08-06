import React, { useState, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { motion, AnimatePresence } from 'framer-motion';
import AIOrb from './components/AIOrb';
import BentoGrid from './components/BentoGrid';
import TutorInterface from './components/TutorInterface';
import { useGuitarTutor } from './hooks/useGuitarTutor';

function App() {
  const tutor = useGuitarTutor();
  const [mode, setMode] = useState('landing'); // 'landing' | 'tutor'

  const startTutorMode = () => {
    setMode('tutor');
  };

  const handleSuggestionClick = (prompt) => {
    startTutorMode();
    // Small delay allows the tutor mode to animate in before the message pops up
    setTimeout(() => {
      tutor.sendTextMessage(prompt);
    }, 400);
  };

  return (
    <div className="app-container" style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <div className="ambient-background"></div>
      
      {/* 3D Canvas Background Container - Always present but animated */}
      <motion.div 
        animate={{ 
          y: mode === 'tutor' ? '-15vh' : '0vh', // Move orb slightly up in tutor mode
          scale: mode === 'tutor' ? 0.8 : 1
        }}
        transition={{ duration: 1, ease: 'easeInOut' }}
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}
      >
        <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
          <Suspense fallback={null}>
            <AIOrb pipelineStage={tutor.pipelineStage} />
          </Suspense>
        </Canvas>
      </motion.div>

      <AnimatePresence>
        {mode === 'landing' && (
          <motion.div 
            key="landing"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.6 }}
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1, overflowY: 'auto' }}
          >
            <section style={{ height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', pointerEvents: 'none' }}>
              <motion.h1 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                style={{ fontSize: '5rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '1rem', lineHeight: 1.1 }}
              >
                <span className="text-gradient">Master Music with</span><br />
                <span className="text-gradient-neon">Intelligent Feedback</span>
              </motion.h1>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
                style={{ marginTop: '3rem', pointerEvents: 'auto' }}
              >
                <button 
                  className="glass-panel" 
                  onClick={startTutorMode}
                  style={{ padding: '16px 32px', fontSize: '1.1rem', fontWeight: 600, color: '#fff', cursor: 'pointer', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '30px' }}
                >
                  Start Learning Now
                </button>
              </motion.div>
            </section>
            <BentoGrid onSuggestionClick={handleSuggestionClick} />
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {mode === 'tutor' && (
          <motion.div
            key="tutor"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 2 }}
          >
            <TutorInterface tutor={tutor} />
            
            {/* Status indicator */}
            <div style={{ position: 'absolute', top: '24px', right: '24px', display: 'flex', alignItems: 'center', gap: '8px', zIndex: 10 }}>
              <div style={{ 
                width: '10px', height: '10px', borderRadius: '50%', 
                background: tutor.status === 'connected' ? '#34A853' : tutor.status === 'error' ? '#EA4335' : '#FBBC04',
                boxShadow: `0 0 10px ${tutor.status === 'connected' ? '#34A853' : tutor.status === 'error' ? '#EA4335' : '#FBBC04'}`
              }}></div>
              <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                {tutor.status === 'connected' ? 'Connected to Engine' : 'Connecting...'}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
