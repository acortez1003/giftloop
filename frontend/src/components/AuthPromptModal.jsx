import { useState } from 'react';

function AuthPromptModal({ onClose, onLoginSuccess, onRegisterSuccess }) {
    const [login, setLogin] = useState('');
    const [password, setPassword] = useState('');
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [newPassword, setNewPassword] = useState('');
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

    async function handleRegister(e) {
        e.preventDefault();
        
        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, email, password: newPassword})
        });

        const data = await res.json();

        if (res.ok) {
            onRegisterSuccess(data);
            onClose();
        } else {
            setMessage(data.error)
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
            <p>New? Please register an account.</p>
            <form onSubmit={handleRegister}>
                <input
                    placeholder="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    placeholder="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                />
                <button type="submit">Register</button>
            </form>
            {message && <p>{message}</p>}
            <button onClick={onClose}>Cancel</button>
        </div>
        </div>
    );
}

export default AuthPromptModal;