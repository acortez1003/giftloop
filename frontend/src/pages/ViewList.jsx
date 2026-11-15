import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import GuestSelectionPromptModal from "../components/GuestSelectionPromptModal";

function ViewList() {
    const { token } = useParams();

    const [message, setMessage] = useState('');

    const [showGuestPrompt, setShowGuestPrompt] = useState(true);
    const [listData, setListData] = useState(null);
    const [guestData, setGuestData] = useState(null);
    const [userData, setUserData] = useState(null);
    const [needsIdentity, setNeedsIdentity] = useState(false);
    const [isRecipient, setIsRecipient] = useState(false);

    const [giftData, setGiftData] = useState(null);
    const [giftName, setGiftName] = useState('');

    useEffect(() => {
        async function fetchList() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists/${token}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json();
            setListData(data.list);
            setNeedsIdentity(data.needs_identity);
            setUserData(data.your_member_id);
            setGuestData(data.existing_guests);
            setIsRecipient(data.is_recipient)
        }
        fetchList();
    }, [token]);

    useEffect(() => {
        async function fetchGifts() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists/${token}/gifts`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json();
            setGiftData(data.gifts);
        }
        fetchGifts();
    }, [token]);

    async function handleAddGift(e) {
        e.preventDefault();

        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists/${token}/gifts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify( { name: giftName })
        });

        const data = await res.json()

        if (!res.ok) {
            setMessage(data.error)
        }
    }
    
    return (
        <div>
            {!listData ? (
                <p>Loading...</p>
            ) : needsIdentity && showGuestPrompt ? (
                <GuestSelectionPromptModal
                    token={token}
                    existingGuests={guestData}
                    onClose={() => setShowGuestPrompt(false)}
                    onIdentitySuccess={member => {
                        console.log('List member as', member.guest.name);
                    }}
                />
            ) : (
                <div>
                    <h1>Page for {listData.name}</h1>
                    {isRecipient ? (
                        <div>
                        <p>You are the recipient</p>
                        <form onSubmit={handleAddGift}>
                            <input placeholder="gift name" value={giftName} onChange={(e) => setGiftName(e.target.value)}/>
                            <button type="submit">Add Gift</button>
                        </form>
                        </div>
                    ) : (
                        <p>You are a list member</p>
                    )}
                    { giftData && giftData.length > 0 ? (
                        <ul>
                            {giftData.map((gift) => (
                                <li key={gift.id}>{gift.name}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>No gifts to show</p>
                    )}
                </div>
            )}
        </div>
    );
}

export default ViewList;