import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = "http://localhost:8000/api/sessions";

export const useSessions = () => {
  const { token } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSessions = useCallback(async () => {
    if (!token) return;
    try {
      setLoading(true);
      const response = await axios.get(API_URL, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessions(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch sessions");
    } finally {
      setLoading(false);
    }
  }, [token]);

  const createSession = useCallback(async (title = "New Chat") => {
    if (!token) return null;
    try {
      const response = await axios.post(API_URL, { title }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessions(prev => [response.data, ...prev]);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create session");
      return null;
    }
  }, [token]);

  const deleteSession = useCallback(async (sessionId) => {
    if (!token) return false;
    try {
      await axios.delete(`${API_URL}/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete session");
      return false;
    }
  }, [token]);

  const updateSession = useCallback(async (sessionId, newTitle) => {
    if (!token) return null;
    try {
      const response = await axios.put(`${API_URL}/${sessionId}`, { title: newTitle }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessions(prev => prev.map(s => s.id === sessionId ? response.data : s));
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update session");
      return null;
    }
  }, [token]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  // Auto-refresh sessions every 10 seconds to pick up title changes and updated_at
  useEffect(() => {
    if (!token) return;
    const interval = setInterval(() => {
      fetchSessions();
    }, 10000);
    return () => clearInterval(interval);
  }, [token, fetchSessions]);

  return {
    sessions,
    loading,
    error,
    createSession,
    updateSession,
    deleteSession,
    refreshSessions: fetchSessions
  };
};
