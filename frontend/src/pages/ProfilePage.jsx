import React, { useState, useEffect } from 'react';
import { postAPI, commentAPI } from '../api';
import { getUsername } from '../utils/auth';

const ProfilePage = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [imageUrl, setImageUrl] = useState('');
  const [caption, setCaption] = useState('');
  
  const username = getUsername();
  const [commentsByPost, setCommentsByPost] = useState({});

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await postAPI.getProfile(username);
      const loaded = response.data.posts || [];
      setPosts(loaded);
      // Load comments per post (viewer = current username for masking rules)
      const entries = await Promise.all(
        loaded.map(async (p) => {
          try {
            const res = await commentAPI.getComments(p.id, username);
            return [p.id, res.data.comments || []];
          } catch (e) {
            console.error('Comments load failed for post', p.id, e);
            return [p.id, []];
          }
        })
      );
      const map = Object.fromEntries(entries);
      setCommentsByPost(map);
    } catch (err) {
      setError('Failed to load profile. Please try again.');
      console.error('Profile error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!imageUrl.trim()) {
      setError('Please enter an image URL');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      await postAPI.uploadPost(username, imageUrl, caption);
      setSuccess('Post uploaded successfully!');
      setImageUrl('');
      setCaption('');
      fetchProfile(); // Refresh posts
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload post. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-insta-pink border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-6">
      <div className="max-w-4xl mx-auto px-4">
        {/* Profile Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-6 mb-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-insta-purple to-insta-pink flex items-center justify-center text-white text-3xl font-bold">
              {username?.[0]?.toUpperCase() || 'U'}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{username}</h1>
              <p className="text-gray-600">{posts.length} {posts.length === 1 ? 'post' : 'posts'}</p>
            </div>
          </div>

          {/* Upload Form */}
          <div className="border-t pt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload New Post</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <input
                  type="url"
                  placeholder="Image URL"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  disabled={uploading}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-insta-pink focus:border-transparent transition"
                  required
                />
              </div>
              <div>
                <textarea
                  placeholder="Write a caption..."
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  disabled={uploading}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-insta-pink focus:border-transparent transition resize-none"
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              {success && (
                <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg text-sm">
                  {success}
                </div>
              )}

              <button
                type="submit"
                disabled={uploading}
                className="w-full bg-gradient-to-r from-insta-purple to-insta-pink text-white font-semibold py-3 rounded-lg hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? 'Uploading...' : 'Upload Post'}
              </button>
            </form>
          </div>
        </div>

        {/* Posts with Comments (Profile view) */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Your Posts</h2>
          {posts.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-12 text-center">
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No Posts Yet</h3>
              <p className="text-gray-500">Upload your first post above!</p>
            </div>
          ) : (
            <div className="space-y-5">
              {posts.map((post) => (
                <div key={post.id} className="bg-white border border-gray-300 rounded-lg overflow-hidden max-w-sm mx-auto md:max-w-md">
                  {/* Header */}
                  <div className="flex items-center gap-3 px-3 py-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-insta-purple to-insta-pink flex items-center justify-center text-white font-bold text-sm">
                      {username?.[0]?.toUpperCase() || 'U'}
                    </div>
                    <span className="font-semibold text-gray-900 text-sm">{username}</span>
                  </div>

                  {/* Image */}
                  <img
                    src={post.image_url}
                    alt={post.caption || 'Post'}
                    className="w-full aspect-square object-cover"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/600x600/e5e7eb/9ca3af?text=Image+Not+Found';
                    }}
                  />

                  {/* Body */}
                  <div className="px-3 py-2 space-y-2">
                    {/* Caption */}
                    {post.caption && (
                      <div className="text-xs">
                        <span className="font-semibold text-gray-900 mr-2">{username}</span>
                        <span className="text-gray-700">{post.caption}</span>
                      </div>
                    )}

                    {/* Comments */}
                    <div className="space-y-2">
                      {(commentsByPost[post.id] || []).map((comment) => (
                        <div key={comment.id} className="text-xs">
                          <span className="font-semibold text-gray-900 mr-2">{comment.author}</span>
                          <span className="text-gray-700 break-words">{comment.text}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
