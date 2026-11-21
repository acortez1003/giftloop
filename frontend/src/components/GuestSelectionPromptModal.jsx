import { useState } from 'react';

function GuestSelectionPromptModal({ joinUrl, existingGuests, onClose, onIdentitySuccess }) {
    const [existingGuest, setExistingGuest] = useState(null);
    const [message, setMessage] = useState('');
    const [displayName, setDisplayName] = useState('');

    async function handleSelectExisting(e) {
        e.preventDefault();

        const res = await fetch(joinUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ existing_listmember_id: existingGuest})
        });

        const data = await res.json();

        if (res.ok) {
            onIdentitySuccess(data);
            onClose()
        } else {
            setMessage(data.error)
        }
    }

    async function handleNewGuest(e) {
        e.preventDefault();

        const res = await fetch(joinUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name: displayName})
        });

        const data = await res.json();

        if (res.ok) {
            onIdentitySuccess(data);
            onClose()
        } else {
            setMessage(data.error)
        }
    }

    return (
        <div className="modal-overlay">
            <div className="modal">
                <p>Already apart of this list? Choose your name:</p>
                {existingGuests.length > 0 ? (
                    <form id="guest-form" onSubmit={handleSelectExisting}>
                        <select onChange={(e) => setExistingGuest(e.target.value)} required defaultValue="">
                            <option value="" disabled>Select your name</option>
                            {existingGuests.map((guest) => (
                                <option key={guest.id} value={guest.id}>{guest.display_name}</option>
                            ))}
                        </select>
                        <button type="submit">Submit</button>
                    </form>
                ) : (
                    <p>No guests to choose from</p>
                )}
                <p>New? Choose your name</p>
                <form onSubmit={handleNewGuest}>
                    <input 
                        value={displayName} 
                        onChange={(e) => setDisplayName(e.target.value)} 
                        placeholder="Alex" 
                    />
                    <button type="submit">Enter</button>
                </form>
                {message && <p>{message}</p>}
            </div>
        </div>
    );
}

export default GuestSelectionPromptModal;