import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './auth.css';

const SignupPage = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    const result = await signup(email, username, password);
    
    if (result.success) {
      navigate('/chat');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      
      <div className="auth-bg-glow">
        <div className="auth-streak blue"></div>
        <div className="auth-streak rainbow"></div>
      </div>

      <div className="auth-modal">
        <div className="auth-top-row">
          <div className="auth-tabs">
            <button className="auth-tab active">Sign up</button>
            <Link to="/login" className="auth-tab">Sign in</Link>
          </div>
          <Link to="/" className="auth-close-btn" aria-label="Close">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M1 1L13 13M13 1L1 13" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>
          </Link>
        </div>

        <h1 className="auth-heading">Create an account</h1>
        
        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          
          <div className="auth-field has-icon full">
            <span className="icon">
              <svg width="17" height="13" viewBox="0 0 17 13" fill="none" style={{width:'17px', height:'17px'}}><circle cx="8.5" cy="4" r="3" stroke="currentColor" strokeWidth="1.2"/><path d="M2.5 12c0-2.5 3-4.5 6-4.5s6 2 6 4.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/></svg>
            </span>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Choose a username"
            />
          </div>

          <div className="auth-field has-icon full">
            <span className="icon">
              <svg width="17" height="13" viewBox="0 0 17 13" fill="none"><path d="M1.5 1.5h14a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-14a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1z" stroke="currentColor" strokeWidth="1.2"/><path d="M1 2.2l7.5 5.8L16 2.2" stroke="currentColor" strokeWidth="1.2"/></svg>
            </span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
            />
          </div>

          <div className="auth-field has-icon full" style={{marginBottom: '22px'}}>
            <span className="icon">
              <svg width="14" height="16" viewBox="0 0 14 16" fill="none"><rect x="1" y="6.5" width="12" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.2"/><path d="M3.5 6.5V4a3.5 3.5 0 0 1 7 0v2.5" stroke="currentColor" strokeWidth="1.2"/></svg>
            </span>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="auth-cta"
          >
            {loading ? 'Creating account...' : 'Create an account'}
          </button>
        </form>

        <p className="auth-footer-text">
          By creating an account, you agree to our <a href="#">Terms & Service</a>
        </p>
      </div>
    </div>
  );
};

export default SignupPage;
