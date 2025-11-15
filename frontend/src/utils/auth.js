export const getUsername = () => {
  return localStorage.getItem('username');
};

export const setUsername = (username) => {
  localStorage.setItem('username', username);
};

export const removeUsername = () => {
  localStorage.removeItem('username');
};

export const isAuthenticated = () => {
  return !!getUsername();
};
