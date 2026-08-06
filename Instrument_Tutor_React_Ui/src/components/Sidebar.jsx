import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Pencil, Trash2, Check, X, Search, LogOut } from 'lucide-react';

const SWATCH_COLORS = ['#5f7ce8', '#f0a25c', '#e0608a', '#3aab8e', '#9b72cb'];

// Helper to group sessions by date
function groupSessionsByDate(sessions) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const sevenDaysAgo = new Date(today);
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

  const groups = {
    today: [],
    yesterday: [],
    thisWeek: [],
    older: []
  };

  sessions.forEach(session => {
    const sessionDate = new Date(session.updated_at || session.created_at);
    if (sessionDate >= today) {
      groups.today.push(session);
    } else if (sessionDate >= yesterday) {
      groups.yesterday.push(session);
    } else if (sessionDate >= sevenDaysAgo) {
      groups.thisWeek.push(session);
    } else {
      groups.older.push(session);
    }
  });

  return groups;
}

const Sidebar = ({ sessions, currentSessionId, onSelectSession, onCreateSession, onDeleteSession, onUpdateSession }) => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const editInputRef = useRef(null);

  useEffect(() => {
    if (editingId && editInputRef.current) {
      editInputRef.current.focus();
    }
  }, [editingId]);

  const handleSaveEdit = (e) => {
    e.stopPropagation();
    if (editTitle.trim() && onUpdateSession) {
      onUpdateSession(editingId, editTitle.trim());
    }
    setEditingId(null);
  };

  const cancelEdit = (e) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const filteredSessions = sessions.filter(s => 
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const groups = groupSessionsByDate(filteredSessions);

  const renderSessionItem = (session, globalIndex) => {
    const swatchColor = SWATCH_COLORS[globalIndex % SWATCH_COLORS.length];
    const initial = session.title ? session.title.charAt(0).toUpperCase() : 'C';
    const isActive = currentSessionId === session.id;

    return (
      <div
        key={session.id}
        onClick={() => {
          if (editingId !== session.id) onSelectSession(session.id);
        }}
        className={`chat-item ${isActive ? 'active' : ''}`}
      >
        <div className="swatch" style={{ background: swatchColor }}>
          {initial}
        </div>
        
        {editingId === session.id ? (
          <div style={{flex: 1, display: 'flex', alignItems: 'center', gap: '4px', minWidth: 0}}>
            <input
              ref={editInputRef}
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSaveEdit(e);
                if (e.key === 'Escape') cancelEdit(e);
              }}
              style={{
                flex: 1, background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.2)', 
                borderRadius: '4px', padding: '2px 6px', fontSize: '13px', color: '#fff', outline: 'none', width: '100%'
              }}
              onClick={(e) => e.stopPropagation()}
            />
            <button onClick={handleSaveEdit} style={{color: '#4ade80', background: 'none', border: 'none', cursor: 'pointer', padding: 0}}><Check size={14} /></button>
            <button onClick={cancelEdit} style={{color: '#9ca3af', background: 'none', border: 'none', cursor: 'pointer', padding: 0}}><X size={14} /></button>
          </div>
        ) : (
          <>
            <span className="label">
              {session.title}
            </span>
            
            <div className="dots" style={{ opacity: isActive ? 1 : undefined }}>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setEditingId(session.id);
                  setEditTitle(session.title);
                }}
                style={{background: 'none', border: 'none', color: isActive ? '#fff' : 'inherit', cursor: 'pointer', padding: '2px'}}
                title="Rename"
              >
                <Pencil size={13} />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(session.id);
                }}
                style={{background: 'none', border: 'none', color: isActive ? '#fff' : 'inherit', cursor: 'pointer', padding: '2px'}}
                title="Delete"
              >
                <Trash2 size={13} />
              </button>
            </div>
          </>
        )}
      </div>
    );
  };

  // Build a flat index for consistent swatch colors
  const allFiltered = [...groups.today, ...groups.yesterday, ...groups.thisWeek, ...groups.older];
  const getGlobalIndex = (session) => allFiltered.indexOf(session);

  return (
    <div className="sidebar">
      
      <div className="sidebar-head">
        <h2>Chat</h2>
        <span 
          className="icon-btn-plain"
          onClick={() => setShowSearch(!showSearch)}
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><circle cx="6.5" cy="6.5" r="5" stroke="currentColor" strokeWidth="1.3"/><path d="M13 13l-3-3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>
        </span>
      </div>

      {showSearch && (
        <div style={{position: 'relative', marginBottom: '16px'}}>
          <div style={{position: 'absolute', inset: '0 0 0 10px', display: 'flex', alignItems: 'center', pointerEvents: 'none'}}>
            <Search size={14} style={{color: '#9a9aa3'}} />
          </div>
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', 
              borderRadius: '9px', padding: '6px 12px 6px 30px', fontSize: '13px', color: '#fff', outline: 'none'
            }}
          />
        </div>
      )}

      <button className="new-chat-btn" onClick={onCreateSession}>
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M6.5 1.5v10M1.5 6.5h10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>
        New Chat
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M2 11L11 2M11 2H5M11 2V8" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg>
      </button>

      <div className="chat-list custom-scrollbar">
        {/* Today */}
        {groups.today.length > 0 && (
          <>
            <div className="section-label">
              <span className="left">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.1"/><path d="M6 3v3.5l2 1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round" strokeLinejoin="round"/></svg>
                Today
              </span>
            </div>
            {groups.today.map(session => renderSessionItem(session, getGlobalIndex(session)))}
          </>
        )}

        {/* Yesterday */}
        {groups.yesterday.length > 0 && (
          <>
            <div className="section-label" style={{marginTop: groups.today.length > 0 ? '14px' : '4px'}}>
              <span className="left">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><rect x="1" y="2" width="10" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.1"/><path d="M3.5 1v2M8.5 1v2M1 5h10" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/></svg>
                Yesterday
              </span>
            </div>
            {groups.yesterday.map(session => renderSessionItem(session, getGlobalIndex(session)))}
          </>
        )}

        {/* This Week */}
        {groups.thisWeek.length > 0 && (
          <>
            <div className="section-label" style={{marginTop: (groups.today.length > 0 || groups.yesterday.length > 0) ? '14px' : '4px'}}>
              <span className="left">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 1l1.5 3.2L11 4.7 8.5 7 9 10.5 6 8.8 3 10.5 3.5 7 1 4.7l3.5-.5L6 1z" stroke="currentColor" strokeWidth="1.1" strokeLinejoin="round"/></svg>
                This Week
              </span>
            </div>
            {groups.thisWeek.map(session => renderSessionItem(session, getGlobalIndex(session)))}
          </>
        )}

        {/* Older */}
        {groups.older.length > 0 && (
          <>
            <div className="section-label" style={{marginTop: (groups.today.length > 0 || groups.yesterday.length > 0 || groups.thisWeek.length > 0) ? '14px' : '4px'}}>
              <span className="left">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M10.5 6A4.5 4.5 0 1 1 1.5 6a4.5 4.5 0 0 1 9 0z" stroke="currentColor" strokeWidth="1.1"/><path d="M6 3.5v3l2 1" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round" strokeLinejoin="round"/></svg>
                Older
              </span>
            </div>
            {groups.older.map(session => renderSessionItem(session, getGlobalIndex(session)))}
          </>
        )}

        {/* Empty state */}
        {filteredSessions.length === 0 && !searchQuery && (
          <div style={{textAlign: 'center', color: '#6e6e73', fontSize: '12px', padding: '20px 0'}}>
            No chats yet
          </div>
        )}
        {filteredSessions.length === 0 && searchQuery && (
          <div style={{textAlign: 'center', color: '#6e6e73', fontSize: '12px', padding: '20px 0'}}>
            No results for "{searchQuery}"
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <div 
          onClick={() => navigate('/settings')}
          className="sidebar-footer-item"
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          <div style={{width: '32px', display: 'flex', justifyContent: 'center'}}>
             <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9a9aa3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
          </div>
          <div style={{flex: 1, fontSize: '13px', fontWeight: 600, color: '#c4c6d6'}}>
            Settings
          </div>
        </div>

        <div 
          onClick={logout}
          className="sidebar-footer-item"
          style={{ borderTop: '1px solid rgba(255,255,255,0.05)', marginTop: '4px' }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          <div style={{
            width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, #9db6f7, #5f7ce8)', 
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 'bold', fontSize: '13px'
          }}>
            {user?.username ? user.username[0].toUpperCase() : 'U'}
          </div>
          <div style={{flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontSize: '13px', fontWeight: 600, color: '#fff'}}>
            {user?.username || 'User'}
          </div>
          <LogOut size={15} color="#9a9aa3" />
        </div>
      </div>
      
    </div>
  );
};

export default Sidebar;
