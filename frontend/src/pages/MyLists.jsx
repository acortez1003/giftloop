import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'

function MyLists() {
    const navigate = useNavigate()
    const [myLists, setMyLists] = useState(null);
    const [joinedLists, setJoinedLists] = useState(null);

    useEffect(() => {
        async function fetchMyLists() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/users/me/lists`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json()
            setMyLists(data.owned_lists);
            setJoinedLists(data.joined_lists);
        }
        fetchMyLists();
    }, []);

    async function handleViewList(token) {
        navigate(`/lists/${token}`);
    }

    return (
        <div>
            <h2>My Lists</h2>
            {myLists && myLists.length > 0 ? (
                <ul>
                    {myLists.map((list) => (
                        <li key={list.id}>
                            {list.name}
                            <button onClick={() => handleViewList(list.token)}>
                                View List
                            </button>
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
        </div>
    );
}

export default MyLists;