import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import GuestSelectionPromptModal from "../components/GuestSelectionPromptModal";

function ViewGroup() {
    const navigate = useNavigate();
    const { token } = useParams();
    const [groupData, setGroupData] = useState(null);
    const [needsIdentity, setNeedsIdentity] = useState(false);
    const [myData, setMyData] = useState(null);
    const [guestData, setGuestData] = useState(null);
    const [memberListData, setMemberListData] = useState(null);
    const [myListData, setMyListData] = useState(null);
    const [showGuestPrompt, setShowGuestPrompt] = useState(true);

    useEffect(() => {
        async function fetchGroup() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/groups/${token}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json();
            setGroupData(data.group);
            setNeedsIdentity(data.needs_identity);
            setMyData(data.your_data);
            setGuestData(data.existing_guests);
        }
        fetchGroup();
    }, [token]);

    useEffect(() => {
        async function fetchLists() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/groups/${token}/lists`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json();
            setMyListData(data.my_list);
            setMemberListData(data.member_lists);
        }
        fetchLists();
    }, [token]);

    async function handleCreateList(group_id, name) {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name: name, group_id: group_id})
        });
        const data = await res.json();
        if (!res.ok) {
            console.log(data.error);
        } 
    }

    async function handleViewList(token) {
        navigate(`/lists/${token}`);
    }

    async function handleDeleteList(list_id) {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists/${list_id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        const data = await res.json();
        if (!res.ok) {
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
                        <li>
                        {myData.name}
                        <button onClick={() => handleViewList(myListData.token)}>View List</button>
                        <button onClick={() => handleDeleteList(myListData.id)}>Delete</button>
                        </li>
                    ) : (
                        <div>
                        <p>You don't have a list for this group yet.</p>
                        <button onClick={() => handleCreateList(groupData.id, `${groupData.name} - ${myData.name}`)}>
                            Create List
                        </button>
                        </div>
                    )}
                    <h3>Group Member Lists</h3>
                    { memberListData && memberListData.length > 0 ? (
                        <ul>
                            {memberListData.map((list) => (
                                <li key={list.id}>
                                    {list.owner_name}
                                    <button type="button" onClick={() => handleViewList(list.token)}>View List</button>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No list data</p>
                    )}
                </div>
            )}
        </div>
    );
}

export default ViewGroup;