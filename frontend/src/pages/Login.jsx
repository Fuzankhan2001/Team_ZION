import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const res = await api.post('/auth/token', formData);
            localStorage.setItem('token', res.data.access_token);
            localStorage.setItem('role', res.data.role);
            localStorage.setItem('facility_id', res.data.facility_id);
            navigate('/');
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (err.response?.status === 401) {
                setError(detail || 'Invalid username or password.');
            } else {
                setError('Server error. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#0f172a' }}>
            <form onSubmit={handleSubmit} style={{ background: '#1e293b', padding: '2rem', borderRadius: '12px', width: '360px' }}>
                <h2 style={{ color: '#fff', marginBottom: '1.5rem', textAlign: 'center' }}>Login</h2>

                {error && (
                    <div style={{ background: '#450a0a', border: '1px solid #dc2626', color: '#fca5a5', padding: '10px 12px', borderRadius: '6px', marginBottom: '16px', fontSize: '0.875rem' }}>
                        {error}
                    </div>
                )}

                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    style={{ width: '100%', padding: '10px', marginBottom: '12px', borderRadius: '6px', border: '1px solid #334155', background: '#0f172a', color: '#fff', boxSizing: 'border-box' }}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{ width: '100%', padding: '10px', marginBottom: '16px', borderRadius: '6px', border: '1px solid #334155', background: '#0f172a', color: '#fff', boxSizing: 'border-box' }}
                />
                <button
                    type="submit"
                    disabled={loading}
                    style={{ width: '100%', padding: '10px', background: loading ? '#1d4ed8' : '#3b82f6', color: '#fff', border: 'none', borderRadius: '6px', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 'bold', opacity: loading ? 0.7 : 1 }}
                >
                    {loading ? 'Signing in...' : 'Sign In'}
                </button>
            </form>
        </div>
    );
}
