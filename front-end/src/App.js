import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DocumentsPage from './pages/DocumentsPage';
import OrganizationPage from './pages/OrganizationPage';
import OrganizationSetupPage from './pages/OrganizationSetupPage';
import { chakraTheme } from './theme';
import './App.css';
import './styles/chat.css';

function App() {
  return (
    <ChakraProvider theme={chakraTheme}>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Protected routes with Layout */}
              <Route 
                path="/" 
                element={
                  <Layout>
                    <DashboardPage />
                  </Layout>
                } 
              />
              
              <Route 
                path="/dashboard" 
                element={
                  <Layout>
                    <DashboardPage />
                  </Layout>
                } 
              />
              
              <Route 
                path="/chat" 
                element={
                  <Layout>
                    <ChatPage />
                  </Layout>
                } 
              />
              
              <Route 
                path="/documents" 
                element={
                  <Layout>
                    <DocumentsPage />
                  </Layout>
                } 
              />

              <Route 
                path="/organization" 
                element={
                  <Layout>
                    <OrganizationPage />
                  </Layout>
                } 
              />

              <Route 
                path="/organization/setup" 
                element={
                  <Layout>
                    <OrganizationSetupPage />
                  </Layout>
                } 
              />
              
              {/* Fallback route */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </ChakraProvider>
  );
}

export default App;
