import { useState } from 'react';

function App() {
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
      setMessage(`Logged in as ${data.username}`);
    } else {
      setMessage(data.error);
    }
  }

  return (
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
      <p>{message}</p>
    </form>
  );
}

export default App;