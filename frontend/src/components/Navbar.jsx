import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { removeUsername, getUsername } from '../utils/auth';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const username = getUsername();

  const handleLogout = () => {
    removeUsername();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="fixed top-0 left-0 right-0 bg-white border-b border-gray-300 z-50">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link to="/feed" className="text-2xl font-bold bg-gradient-to-r from-insta-purple to-insta-pink bg-clip-text text-transparent">
          ToxicFilter
        </Link>

        {/* Navigation Icons */}
        <div className="flex items-center gap-6">
          <Link
            to="/feed"
            className={`flex flex-col items-center gap-1 ${
              isActive('/feed') ? 'text-insta-pink' : 'text-gray-700 hover:text-gray-900'
            }`}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span className="text-xs hidden md:block">Feed</span>
          </Link>

          <Link
            to="/profile"
            className={`flex flex-col items-center gap-1 ${
              isActive('/profile') ? 'text-insta-pink' : 'text-gray-700 hover:text-gray-900'
            }`}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span className="text-xs hidden md:block">Profile</span>
          </Link>

          <button
            onClick={handleLogout}
            className="flex flex-col items-center gap-1 text-gray-700 hover:text-red-500"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span className="text-xs hidden md:block">Logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
