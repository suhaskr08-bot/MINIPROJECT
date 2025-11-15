import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api';
import { setUsername, isAuthenticated } from '../utils/auth';

const LoginPage = () => {
  const [username, setUsernameInput] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  React.useEffect(() => {
    if (isAuthenticated()) {
      navigate('/feed');
    }
  }, [navigate]);

  const handleAuth = async (e, isCreatingAccount = false) => {
    if (e) e.preventDefault();
    setError('');
    
    if (!username.trim() || !password.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await authAPI.login(username, password);
      if (response.data.message) {
        setUsername(username);
        navigate('/feed');
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Authentication failed. Please try again.';
      if (isCreatingAccount && errorMsg.includes('Invalid credentials')) {
        setError('Username already exists. Please use a different username or try logging in.');
      } else if (!isCreatingAccount && errorMsg.includes('Invalid credentials')) {
        setError('Invalid password. Please try again.');
      } else {
        setError(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-insta-purple via-insta-pink to-insta-blue bg-clip-text text-transparent mb-2">
            ToxicFilter
          </h1>
          <p className="text-gray-600 text-sm">Safer social media environment.</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={(e) => handleAuth(e, false)} className="space-y-5">
            <div>
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsernameInput(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-insta-pink focus:border-transparent transition"
                disabled={loading}
              />
            </div>

            <div>
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-insta-pink focus:border-transparent transition"
                disabled={loading}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-insta-purple to-insta-pink text-white font-semibold py-3 rounded-lg hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Loading...' : 'Login'}
              </button>
              <button
                type="button"
                onClick={(e) => handleAuth(e, true)}
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-insta-purple to-insta-pink text-white font-semibold py-3 rounded-lg hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Loading...' : 'Create Account'}
              </button>
            </div>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            <p>New user? Just enter your details and we'll create an account for you!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
