import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

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
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    setToken(data.access_token);
    setUser({ id: data.user_id, username: data.username });
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify({ id: data.user_id, username: data.username }));
  };

  const register = async (username, email, password, fullName) => {
    const data = await authService.register(username, email, password, fullName);
    setToken(data.access_token);
    setUser({ id: data.id, username: data.username, email: data.email });
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify({ id: data.id, username: data.username, email: data.email }));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
