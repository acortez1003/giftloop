import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'
import AuthPromptModal from "../components/AuthPromptModal";
import GuestNamePromptModal from "../components/GuestNamePromptModal";

function MyLists() {
    const navigate = useNavigate();
    const [myLists, setMyLists] = useState(null);
    const [joinedLists, setJoinedLists] = useState(null);
    const [listName, setListName] = useState('');
    const [pendingListToken, setPendingListToken] = useState(null);

    const [joinedGroups, setJoinedGroups] = useState(null);
    const [myGroups, setMyGroups] = useState(null);
    const [groupName, setGroupName] = useState('');

    const [showAuthPrompt, setShowAuthPrompt] = useState(false);
    const [showGuestPrompt, setShowGuestPrompt] = useState(false);

    // List functions
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

    useEffect(() => {
        async function fetchMyLists() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/users/me/lists`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json();
            setMyLists(data.owned_lists);
            setJoinedLists(data.joined_lists);
        }
        fetchMyLists();
    }, []);

    async function handleViewList(token) {
        navigate(`/lists/${token}`);
    }

    async function handleDeleteList(list_id) {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists/${list_id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        if(res.ok) {
            setMyLists((prev) => prev.filter((l) => l.id !== list_id));
        } else {
            const data = await res.json();
            console.log(data.error);
        }
    }

    // Group Functions
    useEffect(() => {
        async function fetchMyGroups() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/users/me/groups`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json()
            setMyGroups(data.owned_groups);
            setJoinedGroups(data.joined_groups);
        }
        fetchMyGroups();
    }, []);

    async function handleCreateGroup(e) {
        e.preventDefault();

        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/groups`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name: groupName })
        });

        if (res.status === 401) {
            setShowAuthPrompt(true);
            return;
        }

        const data = await res.json();

        navigate(`/groups/${data.token}`);
    }

    async function handleViewGroup(token) {
        navigate(`/groups/${token}`);
    }

    async function handleDeleteGroup(group_id) {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/groups/${group_id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        if(res.ok) {
            setMyGroups((prev) => prev.filter((g) => g.id !== group_id));
        } else {
            const data = await res.json();
            console.log(data.error);
        }
    }

    return (
        <div>
            <h1>Welcome to GiftLoop</h1>
            <form onSubmit={handleCreateList}>
                <input value={listName} onChange={(e) => setListName(e.target.value)} placeholder="List name" />
                <button type="submit">Create List</button>
            </form>

            {showGuestPrompt && (
            <GuestNamePromptModal
                token={pendingListToken}
                onClose={() => setShowGuestPrompt(false)}
                onNameSuccess={(data) => {
                    navigate(`/lists/${pendingListToken}`);
                }}
            />
            )}

            <h2>My Lists</h2>
            {myLists && myLists.length > 0 ? (
                <ul>
                    {myLists.map((list) => (
                        <li key={list.id}>
                            {list.name}
                            <button onClick={() => handleViewList(list.token)}>View List</button>
                            <button onClick={() => handleDeleteList(list.id)}>Delete</button>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>You have no lists</p>
            )}

            <h2>Joined Lists</h2>
            {joinedLists && joinedLists.length > 0 ? (
                <ul>
                    {joinedLists.map((list) => (
                        <li key={list.id}>
                            {list.name}
                            <button onClick={() => handleViewList(list.token)}>
                                View List
                            </button>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>You haven't joined any lists</p>
            )}

            <h2>My Groups</h2>
            <form onSubmit={handleCreateGroup}>
                <input value={groupName} onChange={(e) => setGroupName(e.target.value)} placeholder="Group name" />
                <button type="submit">Create Group</button>
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

            {myGroups && myGroups.length > 0 ? (
                <ul>
                    {myGroups.map((group) => (
                        <li key={group.id}>
                            {group.name}
                            <button onClick={() => handleViewGroup(group.token)}>View Group</button>
                            <button onClick={() => handleDeleteGroup(group.id)}>Delete</button>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>You have no groups</p>
            )}
            <h2>Joined Groups</h2>
            {joinedGroups && joinedGroups.length > 0 ? (
                <ul>
                    {joinedGroups.map((group) => (
                        <li key={group.id}>
                            {group.name}
                            <button onClick={() => handleViewGroup(group.token)}>
                                View Group
                            </button>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>You haven't joined any groups</p>
            )}
        </div>
    );
}

export default MyLists;