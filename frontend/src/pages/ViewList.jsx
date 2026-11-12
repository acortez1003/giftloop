import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import GuestSelectionPromptModal from "../components/GuestSelectionPromptModal";

function ViewList() {
    const { token } = useParams();
    const [showGuestPrompt, setShowGuestPrompt] = useState(true);
    const [listData, setListData] = useState(null);
    const [guestData, setGuestData] = useState(null);
    const [userData, setUserData] = useState(null);
    const [needsIdentity, setNeedsIdentity] = useState(false);
    const [isRecipient, setIsRecipient] = useState(false);

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
                        <p>You are the recipient</p>
                    ) : (
                        <p>You are a list member</p>
                    )}
                </div>
            )}
        </div>
    );
}

export default ViewList;