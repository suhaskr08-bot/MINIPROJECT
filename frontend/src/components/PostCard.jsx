import React, { useState, useEffect } from 'react';
import { postAPI, commentAPI } from '../api';
import { getUsername } from '../utils/auth';
import ToxicityModal from './ToxicityModal';

const PostCard = ({ post, onLikeUpdate }) => {
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [loading, setLoading] = useState(false);
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(post.likes || 0);
  const [showModal, setShowModal] = useState(false);
  const [pendingComment, setPendingComment] = useState(null);
  const [warningDetails, setWarningDetails] = useState(null);
  const username = getUsername();

  useEffect(() => {
    fetchComments();
  }, [post.id]);

  const fetchComments = async () => {
    try {
      const response = await commentAPI.getComments(post.id, username);
      setComments(response.data.comments || []);
    } catch (err) {
      console.error('Failed to fetch comments:', err);
    }
  };

  const handleLike = async () => {
    try {
      const response = await postAPI.likePost(username, post.id);
      const newLikeCount = response.data.likes;
      setLikeCount(newLikeCount);
      setLiked(!liked);
      if (onLikeUpdate) onLikeUpdate(post.id, newLikeCount);
    } catch (err) {
      console.error('Failed to like post:', err);
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    setLoading(true);
    try {
      const response = await commentAPI.postComment(username, post.id, commentText, false);
      // Backend now returns a warning object without status when toxic:
      // { toxicity: 'toxic', toxicity_score, toxicity_type }
      if (response.data && response.data.toxicity === 'toxic') {
        // Show toxicity warning modal
        setPendingComment(commentText);
        setWarningDetails({
          dominant_category: response.data.toxicity_type,
          combined_score: response.data.toxicity_score,
        });
        setShowModal(true);
      } else {
        // Comment posted successfully
        setCommentText('');
        setWarningDetails(null);
        fetchComments();
      }
    } catch (err) {
      console.error('Failed to post comment:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmToxicComment = async () => {
    setShowModal(false);
    setLoading(true);
    try {
      await commentAPI.postComment(username, post.id, pendingComment, true);
      setCommentText('');
      setPendingComment(null);
      setWarningDetails(null);
      fetchComments();
    } catch (err) {
      console.error('Failed to post confirmed comment:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelToxicComment = () => {
    setShowModal(false);
    setPendingComment(null);
    setWarningDetails(null);
  };

  return (
    <>
      <div className="bg-white border border-gray-300 rounded-lg mb-6 overflow-hidden">
        {/* Post Header */}
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-insta-purple to-insta-pink flex items-center justify-center text-white font-bold">
            {post.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <span className="font-semibold text-gray-900">{post.username || 'Unknown'}</span>
        </div>

        {/* Post Image */}
        <img
          src={post.image_url}
          alt={post.caption || 'Post'}
          className="w-full aspect-square object-cover"
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/600x600/e5e7eb/9ca3af?text=Image+Not+Found';
          }}
        />

        {/* Action Buttons */}
        <div className="px-4 py-3 space-y-3">
          <div className="flex items-center gap-4">
            <button
              onClick={handleLike}
              className={`transition-colors ${liked ? 'text-red-500' : 'text-gray-700 hover:text-red-500'}`}
            >
              <svg className="w-7 h-7" fill={liked ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </button>
            <button className="text-gray-700 hover:text-gray-900">
              <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </button>
          </div>

          {/* Like Count */}
          {likeCount > 0 && (
            <div className="font-semibold text-sm text-gray-900">
              {likeCount} {likeCount === 1 ? 'like' : 'likes'}
            </div>
          )}

          {/* Caption */}
          {post.caption && (
            <div className="text-sm">
              <span className="font-semibold text-gray-900 mr-2">{post.username}</span>
              <span className="text-gray-700">{post.caption}</span>
            </div>
          )}

          {/* Comments */}
          <div className="space-y-3">
            {comments.map((comment) => {
              const isMine = comment.author === username;
              return (
                <div key={comment.id} className="text-sm group">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <span className="font-semibold text-gray-900 mr-2">{comment.author}</span>
                      <span className="text-gray-700 break-words">{comment.text}</span>
                    </div>
                    {isMine && (
                      <button
                        onClick={async () => {
                          if (!confirm('Delete this comment?')) return;
                          try {
                            await commentAPI.deleteComment(username, comment.id);
                            fetchComments();
                          } catch (err) {
                            console.error('Failed to delete comment:', err);
                          }
                        }}
                        className="opacity-70 group-hover:opacity-100 text-gray-400 hover:text-red-600 transition"
                        title="Delete comment"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                          <path fillRule="evenodd" d="M16.5 4.478V5.25h3.75a.75.75 0 010 1.5h-.824l-1.07 12.063A2.25 2.25 0 0116.115 21H7.885a2.25 2.25 0 01-2.241-2.187L4.573 6.75H3.75a.75.75 0 010-1.5H7.5v-.772C7.5 3.336 8.336 2.5 9.228 2.5h5.544c.892 0 1.728.836 1.728 1.978zM9 9.75a.75.75 0 011.5 0v7.5a.75.75 0 01-1.5 0v-7.5zm4.5 0a.75.75 0 011.5 0v7.5a.75.75 0 01-1.5 0v-7.5z" clipRule="evenodd" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Comment Input */}
          <form onSubmit={handleCommentSubmit} className="flex items-center gap-2 pt-2 border-t border-gray-200">
            <input
              type="text"
              placeholder="Add a comment..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              disabled={loading}
              className="flex-1 outline-none text-sm text-gray-700 placeholder-gray-400"
            />
            <button
              type="submit"
              disabled={loading || !commentText.trim()}
              className="text-insta-pink font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:text-insta-purple transition"
            >
              {loading ? 'Posting...' : 'Post'}
            </button>
          </form>
        </div>
      </div>

      <ToxicityModal
        isOpen={showModal}
        onClose={handleCancelToxicComment}
        onConfirm={handleConfirmToxicComment}
        message={pendingComment ? `Your comment may contain sensitive content. Do you still want to post it?` : ''}
        details={warningDetails}
      />
    </>
  );
};

export default PostCard;
