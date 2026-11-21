import { useState } from 'react';

function GuestNamePromptModal({ token, onClose, onNameSuccess }) {
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();

    if (!name) {
      setMessage("Please enter a name");
      return;
    }

    const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists/${token}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ display_name: name })
    });

    const data = await res.json();

    if (res.ok) {
      onNameSuccess(data);
      onClose();
    } else {
      setMessage(data.error);
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <p>Please enter a name.</p>
        <form onSubmit={handleSubmit}>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Alex" />
          <button type="submit">Enter</button>
        </form>
        {message && <p>{message}</p>}
      </div>
    </div>
  );
}

export  default GuestNamePromptModal;