import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import GuestSelectionPromptModal from "../components/GuestSelectionPromptModal";

function ViewGroup() {
    const { token } = useParams();
    const [groupData, setGroupData] = useState(null);
    const [needsIdentity, setNeedsIdentity] = useState(false);
    const [guestData, setGuestData] = useState(null);
    const [memberListData, setMemberListData] = useState(null);
    const [myListData, setMyListData] = useState(null);
    const [showGuestPrompt, setShowGuestPrompt] = useState(true);
    const [listName, setListName] = useState('');

    useEffect(() => {
        async function fetchGroup() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/groups/${token}`, {
                method: ['GET'],
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json();
            setGroupData(data.group);
            setNeedsIdentity(data.needs_identity);
            setGuestData(data.existing_guests);
        }
        fetchGroup();
    }, [token]);

    useEffect(() => {
        async function fetchLists() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/groups/${token}/lists`, {
                method: ['GET'],
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json();
            setMyListData(data.my_list);
            setMemberListData(data.member_lists);
        }
        fetchLists();
    }, [token]);

    async function handleCreateList(e) {
        e.preventDefault();

        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists`, {
            method: ['POST'],
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name: listName, group_id: groupData.id})
        });
        const data = await res.json();
        if (res.ok) {
            setMyListData((prev) => [...prev, data]);
        } else {
            console.log(data.error);
        }
    }

    return (
        <div>
            {!groupData ? (
                <p>Loading...</p>
            ) : needsIdentity && showGuestPrompt ? (
                <GuestSelectionPromptModal
                    joinUrl={`${import.meta.env.VITE_API_URL}/api/groups/${token}/join`}
                    existingGuests={guestData}
                    onClose={() => setShowGuestPrompt(false)}
                    onIdentitySuccess={member => {
                        console.log('Group member as', member.guest.name);
                    }}
                />
            ) : (
                <div>
                    <h1>Page for {groupData.name}</h1>
                    <h3>My List</h3>
                    { myListData ? (
                        <p>{myListData.name}</p>
                    ) : (
                        <div>
                        <p>You don't have a list for this group yet.</p>
                        <form onSubmit={handleCreateList}>
                            <input value={listName} onChange={(e) => setListName(e.target.value)} placeholder="List name" />
                            <button type="submit">Create List</button>
                        </form>
                        </div>
                    )}
                    <h3>Group Member Lists</h3>
                    { memberListData && memberListData.length > 0 ? (
                        <p>There is list data</p>
                    ) : (
                        <p>No list data</p>
                    )}
                </div>
            )}
        </div>
    );
}

export default ViewGroup;