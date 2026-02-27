import { useState, useEffect } from 'react';
import api from '../services/api';

export default function ChatWidget() {
    const [messages, setMessages] = useState([]);
    const [newMsg, setNewMsg] = useState('');

    useEffect(() => {
        const fetchMsgs = async () => {
            try {
                const res = await api.get('/api/chat/messages');
                setMessages(res.data || []);
            } catch (err) {
                console.error('Failed to fetch messages:', err);
            }
        };
        fetchMsgs();
        const interval = setInterval(fetchMsgs, 3000);
        return () => clearInterval(interval);
    }, []);

    const sendMessage = async () => {
        if (!newMsg.trim()) return;
        try {
            await api.post('/api/chat/send', { message: newMsg });
            setNewMsg('');
        } catch (err) {
            console.error('Send failed:', err);
        }
    };

    return (
        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '1rem', maxHeight: '400px', display: 'flex', flexDirection: 'column' }}>
            <h4 style={{ color: '#fff', marginBottom: '0.5rem' }}>💬 Hospital Network Chat</h4>
            <div style={{ flex: 1, overflowY: 'auto', marginBottom: '0.5rem' }}>
                {messages.map((m, i) => (
                    <div key={i} style={{ padding: '4px 0', borderBottom: '1px solid #334155' }}>
                        <span style={{ color: '#3b82f6', fontWeight: 'bold' }}>{m.sender_name}: </span>
                        <span style={{ color: '#e2e8f0' }}>{m.message_text}</span>
                    </div>
                ))}
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
                <input
                    value={newMsg}
                    onChange={e => setNewMsg(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && sendMessage()}
                    placeholder="Type a message..."
                    style={{ flex: 1, padding: '8px', background: '#0f172a', color: '#fff', border: '1px solid #334155', borderRadius: '6px' }}
                />
                <button onClick={sendMessage} style={{ padding: '8px 16px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>Send</button>
            </div>
        </div>
    );
}
