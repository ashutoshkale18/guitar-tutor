import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeft, Save, Loader2, Music, Target, Brain } from 'lucide-react';

const SettingsPage = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const [formData, setFormData] = useState({
    skill_level: 'Beginner',
    genre: 'Any',
    learning_style: 'Balanced'
  });

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchProfile = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/users/me/memory', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setProfile(data);
          setFormData({
            skill_level: data.preferences?.skill_level || 'Beginner',
            genre: data.preferences?.genre || 'Any',
            learning_style: data.preferences?.learning_style || 'Balanced'
          });
        }
      } catch (err) {
        console.error("Failed to load profile", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [token, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    
    try {
      const response = await fetch('http://localhost:8000/api/users/me/memory', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        setMessage('Settings saved successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage('Failed to save settings.');
      }
    } catch (err) {
      setMessage('Error connecting to server.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#000] flex items-center justify-center relative">
        {/* Ambient Background Light Streaks */}
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
        <Loader2 className="w-8 h-8 text-[#9db6f7] animate-spin relative z-10" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-[#000] overflow-hidden font-sans text-slate-300">
      
      {/* Ambient Background Light Streaks */}
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

      <div style={{ width: '100%', maxWidth: '950px', margin: '4vh auto 0 auto', padding: '40px 24px', position: 'relative', zIndex: 10 }}>
        <button 
          onClick={() => navigate('/chat')}
          style={{ display: 'flex', alignItems: 'center', color: '#9db6f7', cursor: 'pointer', background: 'none', border: 'none', marginBottom: '32px', fontSize: '14px', fontWeight: 500 }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#c1d1ff'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#9db6f7'}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Tutor
        </button>
        
        <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#fff', marginBottom: '32px' }}>My Profile & Settings</h1>
        
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '32px' }}>
          {/* Settings Form */}
          <div style={{ flex: '2 1 500px' }}>
            <div className="bg-white/[0.03] backdrop-blur-2xl rounded-2xl border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.5)]" style={{ padding: '32px', borderRadius: '16px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#fff', marginBottom: '24px', display: 'flex', alignItems: 'center' }}>
                <Brain style={{ width: '20px', height: '20px', marginRight: '12px', color: '#5f7ce8' }} />
                AI Tutor Preferences
              </h2>
              
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <div>
                  <label className="block text-[13px] font-semibold text-[#a6a6ad] mb-2">
                    Skill Level
                  </label>
                  <select 
                    value={formData.skill_level}
                    onChange={(e) => setFormData({...formData, skill_level: e.target.value})}
                    style={{ width: '100%', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '10px', padding: '10px 16px', fontSize: '14px', color: '#fff', outline: 'none', cursor: 'pointer', appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23FFFFFF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 16px center', backgroundSize: '12px' }}
                  >
                    <option value="Beginner" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Beginner</option>
                    <option value="Intermediate" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Intermediate</option>
                    <option value="Advanced" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Advanced</option>
                  </select>
                  <p className="mt-2 text-[12px] text-[#7a7a82]">How the AI explains concepts.</p>
                </div>

                <div>
                  <label className="block text-[13px] font-semibold text-[#a6a6ad] mb-2">
                    Preferred Genre
                  </label>
                  <select 
                    value={formData.genre}
                    onChange={(e) => setFormData({...formData, genre: e.target.value})}
                    style={{ width: '100%', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '10px', padding: '10px 16px', fontSize: '14px', color: '#fff', outline: 'none', cursor: 'pointer', appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23FFFFFF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 16px center', backgroundSize: '12px' }}
                  >
                    <option value="Any" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Any</option>
                    <option value="Rock" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Rock</option>
                    <option value="Pop" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Pop</option>
                    <option value="Blues" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Blues</option>
                    <option value="Classical" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Classical</option>
                    <option value="Jazz" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Jazz</option>
                    <option value="Metal" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Metal</option>
                  </select>
                  <p className="mt-2 text-[12px] text-[#7a7a82]">Influences the songs and riffs the AI recommends.</p>
                </div>

                <div>
                  <label className="block text-[13px] font-semibold text-[#a6a6ad] mb-2">
                    Learning Style
                  </label>
                  <select 
                    value={formData.learning_style}
                    onChange={(e) => setFormData({...formData, learning_style: e.target.value})}
                    style={{ width: '100%', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '10px', padding: '10px 16px', fontSize: '14px', color: '#fff', outline: 'none', cursor: 'pointer', appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23FFFFFF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 16px center', backgroundSize: '12px' }}
                  >
                    <option value="Balanced" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Balanced</option>
                    <option value="Encouraging" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Encouraging & Supportive</option>
                    <option value="Strict" style={{ background: '#1a1c26', color: '#fff', fontSize: '14px' }}>Strict & Technical</option>
                  </select>
                  <p style={{ marginTop: '8px', fontSize: '12px', color: '#7a7a82' }}>Adjusts the tone of the AI Tutor.</p>
                </div>

                <div style={{ paddingTop: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                  <span style={{ fontSize: '13px', fontWeight: 500, color: message.includes('success') ? '#4ade80' : '#f87171' }}>
                    {message}
                  </span>
                  <button
                    type="submit"
                    disabled={saving}
                    style={{
                      display: 'flex', alignItems: 'center', padding: '10px 24px', background: 'linear-gradient(to right, #9db6f7, #5f7ce8)', 
                      color: '#0a0a0e', fontSize: '13px', fontWeight: 'bold', borderRadius: '99px', border: 'none', cursor: saving ? 'not-allowed' : 'pointer',
                      opacity: saving ? 0.5 : 1
                    }}
                  >
                    {saving ? <Loader2 style={{ width: '16px', height: '16px', marginRight: '8px' }} className="animate-spin" /> : <Save style={{ width: '16px', height: '16px', marginRight: '8px' }} />}
                    Save Preferences
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Stats & Progress */}
          <div style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.5)]" style={{ padding: '24px', borderRadius: '16px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center' }}>
                <Target style={{ width: '18px', height: '18px', marginRight: '8px', color: '#4ade80' }} />
                Mastered Chords
              </h2>
              {profile?.learned_chords?.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {profile.learned_chords.map((chord) => (
                    <span key={chord} style={{ padding: '4px 12px', background: 'rgba(74,222,128,0.1)', color: '#86efac', border: '1px solid rgba(74,222,128,0.2)', borderRadius: '7px', fontSize: '12px', fontWeight: 'bold' }}>
                      {chord}
                    </span>
                  ))}
                </div>
              ) : (
                <p style={{ color: '#a6a6ad', fontSize: '13px' }}>Play a chord perfectly 3 times to master it!</p>
              )}
            </div>
            
            <div className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 shadow-[0_10px_40px_rgba(0,0,0,0.5)]" style={{ padding: '24px', borderRadius: '16px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center' }}>
                <Music style={{ width: '18px', height: '18px', marginRight: '8px', color: '#5f7ce8' }} />
                In Progress
              </h2>
              {profile?.chord_counts && Object.keys(profile.chord_counts).length > 0 ? (
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {Object.entries(profile.chord_counts)
                    .filter(([chord, count]) => count < 3 && !profile?.learned_chords?.includes(chord))
                    .map(([chord, count]) => (
                      <li key={chord} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: '#fff', fontWeight: 600, fontSize: '13.5px' }}>{chord}</span>
                        <div style={{ display: 'flex', gap: '6px' }}>
                          {[1, 2, 3].map((step) => (
                            <div 
                              key={step} 
                              style={{ 
                                width: '12px', height: '12px', borderRadius: '50%', 
                                background: step <= count ? '#5f7ce8' : 'rgba(255,255,255,0.1)',
                                boxShadow: step <= count ? '0 0 8px rgba(95,124,232,0.8)' : 'none'
                              }}
                            />
                          ))}
                        </div>
                      </li>
                  ))}
                  {Object.entries(profile.chord_counts).filter(([chord, count]) => count < 3 && !profile?.learned_chords?.includes(chord)).length === 0 && (
                    <p style={{ color: '#a6a6ad', fontSize: '13px' }}>No chords currently in progress.</p>
                  )}
                </ul>
              ) : (
                <p style={{ color: '#a6a6ad', fontSize: '13px' }}>Start playing to track progress.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
