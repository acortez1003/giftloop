import { useState } from 'react';

function AuthPromptModal({ onClose, onLoginSuccess }) {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  async function handleLogin(e) {
    e.preventDefault();

    const res = await fetch(`${import.meta.env.VITE_API_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ login, password })
    });

    const data = await res.json();

    if (res.ok) {
      onLoginSuccess(data);
      onClose();
    } else {
      setMessage(data.error);
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <p>You need to be logged in to create a list.</p>
        <form onSubmit={handleLogin}>
          <input
            placeholder="username or email"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
          />
          <input
            type="password"
            placeholder="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Log in</button>
        </form>
        {message && <p>{message}</p>}
        <button onClick={onClose}>Cancel</button>
      </div>
    </div>
  );
}

export default AuthPromptModal;