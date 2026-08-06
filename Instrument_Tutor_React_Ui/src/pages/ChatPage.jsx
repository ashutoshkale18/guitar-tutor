import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import TutorInterface from '../components/TutorInterface';
import Sidebar from '../components/Sidebar';
import { useGuitarTutor } from '../hooks/useGuitarTutor';
import { useSessions } from '../hooks/useSessions';
import './chat.css';

const ChatPage = () => {
  const { token, loading: authLoading } = useAuth();
  const { sessions, loading: sessionsLoading, createSession, deleteSession, updateSession } = useSessions();
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  // Set initial session or create one if none exist
  useEffect(() => {
    if (!sessionsLoading && sessions.length > 0 && !currentSessionId) {
      setCurrentSessionId(sessions[0].id);
    } else if (!sessionsLoading && sessions.length === 0 && !currentSessionId && token) {
      // Auto-create a session
      createSession().then(newSession => {
        if (newSession) setCurrentSessionId(newSession.id);
      });
    }
  }, [sessionsLoading, sessions, currentSessionId, createSession, token]);

  const tutor = useGuitarTutor(currentSessionId);

  const handleCreateSession = async () => {
    const newSession = await createSession();
    if (newSession) setCurrentSessionId(newSession.id);
  };

  const handleDeleteSession = async (id) => {
    await deleteSession(id);
    if (currentSessionId === id) {
      setCurrentSessionId(null);
    }
  };

  if (authLoading) {
    return <div className="min-h-screen bg-[#0A0A0E] flex items-center justify-center text-white">Loading...</div>;
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="chat-page-container">
      
      {/* Ambient Background Light Streaks (Shared from Auth Theme) */}
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

      <div className="chat-app">
        {isSidebarOpen && (
          <Sidebar 
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSelectSession={setCurrentSessionId}
            onCreateSession={handleCreateSession}
            onDeleteSession={handleDeleteSession}
            onUpdateSession={updateSession}
          />
        )}
        
        {currentSessionId ? (
          <TutorInterface 
            tutor={tutor} 
            toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} 
            isSidebarOpen={isSidebarOpen} 
          />
        ) : (
          <div className="main" style={{justifyContent: 'center', alignItems: 'center', color: '#9a9aa3', position: 'relative'}}>
            <div className="topbar" style={{position: 'absolute', top: 0, left: 0, right: 0, borderBottom: 'none'}}>
               <div className="topbar-left">
                  <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} style={{background: 'none', border: 'none', color: '#fff', cursor: 'pointer', padding: '8px'}}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                  </button>
               </div>
            </div>
            Select or create a chat to begin
          </div>
        )}
      </div>

    </div>
  );
};

export default ChatPage;
