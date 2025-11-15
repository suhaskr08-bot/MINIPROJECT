import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';
import Navbar from './Navbar';

const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <Navbar />
      <div className="pt-16">
        {children}
      </div>
    </>
  );
};

export default ProtectedRoute;
