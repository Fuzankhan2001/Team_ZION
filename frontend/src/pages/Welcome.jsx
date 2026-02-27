import { useNavigate } from 'react-router-dom';

export default function Welcome() {
    const navigate = useNavigate();

    return (
        <div style={{ minHeight: '100vh', background: '#0f172a', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
            <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>Lifelink</h1>
            <p style={{ color: '#94a3b8', marginBottom: '2rem' }}>Hospital Resource Monitoring System</p>
            <button
                onClick={() => navigate('/login')}
                style={{ padding: '12px 32px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '1rem', cursor: 'pointer' }}
            >
                Get Started
            </button>
        </div>
    );
}
