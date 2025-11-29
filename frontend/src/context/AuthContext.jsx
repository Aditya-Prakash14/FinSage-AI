import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    // Check if user is logged in
    const storedUser = localStorage.getItem('finsage_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const register = async (userData) => {
    try {
      setError(null);
      const response = await axios.post(`${API_URL}/api/auth/register`, userData);
      const { user, token } = response.data;
      
      localStorage.setItem('finsage_user', JSON.stringify(user));
      localStorage.setItem('finsage_token', token);
      setUser(user);
      
      return { success: true, user };
    } catch (err) {
      const message = err.response?.data?.message || 'Registration failed';
      setError(message);
      return { success: false, error: message };
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email,
        password,
      });
      const { user, token } = response.data;
      
      localStorage.setItem('finsage_user', JSON.stringify(user));
      localStorage.setItem('finsage_token', token);
      setUser(user);
      
      return { success: true, user };
    } catch (err) {
      const message = err.response?.data?.message || 'Login failed';
      setError(message);
      return { success: false, error: message };
    }
  };

  const logout = () => {
    localStorage.removeItem('finsage_user');
    localStorage.removeItem('finsage_token');
    setUser(null);
  };

  const updateUserProfile = async (profileData) => {
    try {
      setError(null);
      const token = localStorage.getItem('finsage_token');
      const response = await axios.put(
        `${API_URL}/api/auth/profile`,
        profileData,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      const updatedUser = response.data.user;
      localStorage.setItem('finsage_user', JSON.stringify(updatedUser));
      setUser(updatedUser);
      
      return { success: true, user: updatedUser };
    } catch (err) {
      const message = err.response?.data?.message || 'Profile update failed';
      setError(message);
      return { success: false, error: message };
    }
  };

  const value = {
    user,
    loading,
    error,
    register,
    login,
    logout,
    updateUserProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
