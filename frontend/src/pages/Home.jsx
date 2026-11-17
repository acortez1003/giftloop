import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthPromptModal from "../components/AuthPromptModal";
import GuestNamePromptModal from "../components/GuestNamePromptModal";

function Home() {
    const [showAuthPrompt, setShowAuthPrompt] = useState(false);
    const [showGuestPrompt, setShowGuestPrompt] = useState(false);
    const [pendingListToken, setPendingListToken] = useState(null);
    const [listName, setListName] = useState('');
    const navigate = useNavigate();

    async function handleCreateList(e) {
        e.preventDefault();

        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name: listName })
        });

        if (res.status === 401) {
            setShowAuthPrompt(true);
            return;
        }

        const data = await res.json();

        if (data.needs_identity) {
            setPendingListToken(data.token);
            setShowGuestPrompt(true);
            return;
        }

        navigate(`/lists/${data.token}`);
    }

    async function handleMyLists() {
        navigate('/lists');
    }
  
    return (
        <div>
            <h1>Welcome to GiftLoop</h1>
            <button onClick={handleMyLists} type="submit">My Lists</button>
            <form onSubmit={handleCreateList}>
                <input value={listName} onChange={(e) => setListName(e.target.value)} placeholder="List name" />
                <button type="submit">Create List</button>
            </form>

        {showAuthPrompt && (
            <AuthPromptModal 
                onClose={() => setShowAuthPrompt(false)}
                onLoginSuccess={(user) => {
                    console.log('Logged in as', user.username);
                }}
                onRegisterSuccess={(user) => {
                    console.log('Registered as', user.username)
                }}
            />
        )}

        {showGuestPrompt && (
            <GuestNamePromptModal
                token={pendingListToken}
                onClose={() => setShowGuestPrompt(false)}
                onNameSuccess={(data) => {
                    navigate(`/lists/${pendingListToken}`);
                }}
            />
        )}

        </div>
  );
}

export default Home;