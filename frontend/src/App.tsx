import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Reservations from './pages/Reservations';
import NewReservation from './pages/NewReservation';
import PendingRejections from './pages/PendingRejections';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="reservations" element={<Reservations />} />
            <Route path="new-reservation" element={<NewReservation />} />
            <Route path="pending-rejections" element={<PendingRejections />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;