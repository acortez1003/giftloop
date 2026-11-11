import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function ViewList() {
    const { token } = useParams();
    const [listData, setListData] = useState(null);
    const [guestData, setGuestData] = useState(null);
    const [userData, setUserData] = useState(null);
    const [needsIdentity, setNeedsIdentity] = useState(false);

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
        }
        fetchList();
    }, [token]);
    
    return (
        <div>
            {!listData ? (
                <p>Loading...</p>
            ) : needsIdentity ? (
                <p>Choose a guest or enter your name</p>
            ) : (
                <div>
                    <h1>Page for {listData.name}</h1>
                    {listData.recipient_id === userData ? (
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