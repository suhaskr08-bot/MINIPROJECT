import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authAPI = {
  login: (username, password) => 
    api.post('/login', { username, password }),
};

export const postAPI = {
  uploadPost: (username, image_url, caption) =>
    api.post('/upload_post', { username, image_url, caption }),
  
  getFeed: (username) =>
    api.get(`/feed/${username}`),
  
  getProfile: (username) =>
    api.get(`/profile/${username}`),
  
  likePost: (username, post_id) =>
    api.post('/like', { username, post_id }),
};

export const commentAPI = {
  postComment: (username, post_id, text, confirm = false) =>
    api.post('/comment', { username, post_id, text, confirm }),
  
  getComments: (post_id, viewer) =>
    api.get(`/comments/${post_id}`, { params: { viewer } }),

  deleteComment: (username, comment_id) =>
    api.post('/comment/delete', { username, comment_id }),
};

export default api;
