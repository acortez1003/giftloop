import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function ViewList() {
    const { token } = useParams();
    const [listData, setListData] = useState(null);

    useEffect(() => {
        async function fetchList() {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/lists/${token}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json();
            setListData(data);
        }
        fetchList();
    }, [token]);

    if  (!listData) return <p>Loading...</p>;
    
    return <p>List page for {listData.list.name}</p>;
}

export default ViewList;