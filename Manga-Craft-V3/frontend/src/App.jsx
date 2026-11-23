import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Projects from './pages/Projects'
import Memory from './pages/Memory'
import AIStudio from './pages/AIStudio'
import Login from './pages/Login'
import Register from './pages/Register'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="text-center py-12 text-[var(--text-primary)]">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Layout><Home /></Layout>} />
        <Route path="/projects" element={
          <ProtectedRoute>
            <Layout><Projects /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/memory" element={
          <ProtectedRoute>
            <Layout><Memory /></Layout>
          </ProtectedRoute>
        } />
        {/* AI Studio is full-screen (no Layout wrapper) */}
        <Route path="/projects/:projectId/conversation" element={
          <ProtectedRoute>
            <AIStudio />
          </ProtectedRoute>
        } />
        <Route path="/projects/:projectId/conversation/:conversationId" element={
          <ProtectedRoute>
            <AIStudio />
          </ProtectedRoute>
        } />
        <Route path="/chat" element={<Navigate to="/projects" />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
