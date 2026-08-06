import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import AIOrb from './AIOrb';

const HeroSection = () => {
  const navigate = useNavigate();
  return (
    <section className="hero-section" style={{ height: '100vh', position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      
      {/* 3D Canvas Background Container */}
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}>
        <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
          <Suspense fallback={null}>
            <AIOrb />
          </Suspense>
        </Canvas>
      </div>

      {/* Foreground Content */}
      <div style={{ zIndex: 1, textAlign: 'center', pointerEvents: 'none' }}>
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{ fontSize: '5rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '1rem', lineHeight: 1.1 }}
        >
          <span className="text-gradient">Master Music with</span><br />
          <span className="text-gradient-neon">Intelligent Feedback</span>
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto', fontWeight: 300 }}
        >
          Real-time pitch correction, dynamic pacing, and interactive voice guidance powered by advanced LLM architecture.
        </motion.p>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
          style={{ marginTop: '3rem', pointerEvents: 'auto', display: 'flex', gap: '16px', justifyContent: 'center' }}
        >
          <button 
            onClick={() => navigate('/signup')}
            style={{ padding: '16px 32px', fontSize: '1.1rem', fontWeight: 600, color: '#0a0a0e', background: 'linear-gradient(to right, #9db6f7, #5f7ce8)', cursor: 'pointer', border: 'none', borderRadius: '30px', transition: 'all 0.3s' }}
            onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
            onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
          >
            Start Learning Now
          </button>
          
          <button 
            onClick={() => navigate('/login')}
            className="glass-panel" 
            style={{ padding: '16px 32px', fontSize: '1.1rem', fontWeight: 600, color: '#fff', cursor: 'pointer', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '30px', background: 'rgba(255,255,255,0.05)', transition: 'all 0.3s' }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
          >
            Log In
          </button>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div 
        className="floating-element"
        style={{ position: 'absolute', bottom: '40px', zIndex: 1 }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 1 }}
      >
        <div style={{ width: '1px', height: '60px', background: 'linear-gradient(to bottom, var(--neon-blue), transparent)' }}></div>
      </motion.div>
    </section>
  );
};

export default HeroSection;
