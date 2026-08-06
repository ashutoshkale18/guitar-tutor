import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HeroSection from './components/HeroSection';
import ChatPage from './pages/ChatPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import SettingsPage from './pages/SettingsPage';
import { AuthProvider } from './contexts/AuthContext';
import './App.css';

const LandingPage = () => {
  return (
    <div className="relative min-h-screen bg-[#000] overflow-hidden font-sans">
      {/* Ambient Background Light Streaks (Shared from Auth/Chat Theme) */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute opacity-55 blur-[60px]" style={{
          width: '900px', height: '260px', left: '-250px', bottom: '8%',
          background: 'linear-gradient(100deg, rgba(40,90,255,0) 0%, rgba(60,130,255,0.85) 35%, rgba(120,180,255,0.4) 60%, rgba(60,130,255,0) 100%)',
          transform: 'rotate(-7deg)'
        }}></div>
        <div className="absolute opacity-55 blur-[60px]" style={{
          width: '1100px', height: '420px', right: '-320px', top: '18%',
          background: 'linear-gradient(100deg, rgba(255,60,60,0) 0%, rgba(255,70,70,0.75) 18%, rgba(255,150,50,0.7) 34%, rgba(255,220,80,0.55) 48%, rgba(120,210,140,0.55) 64%, rgba(70,180,255,0.55) 82%, rgba(70,180,255,0) 100%)',
          transform: 'rotate(-12deg)'
        }}></div>
      </div>
      
      <HeroSection />
    </div>
  );
};

const App = () => {
  return (
    <div className="min-h-screen bg-gray-950 font-sans selection:bg-indigo-500/30 text-slate-300">
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </div>
  );
};

export default App;
