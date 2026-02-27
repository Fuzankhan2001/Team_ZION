import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Welcome() {
    const navigate = useNavigate();
    const { logout } = useAuth();

    const username = localStorage.getItem('username') || 'User';

    const roles = [
        {
            id: 'hospital',
            label: '🏥 Hospital Admin',
            desc: 'Monitor and manage your facility resources',
            path: '/hospital',
            color: '#3b82f6',
        },
        {
            id: 'ambulance',
            label: '🚑 Ambulance Crew',
            desc: 'Request patient referrals & navigate to hospitals',
            path: '/ambulance',
            color: '#ef4444',
        },
        {
            id: 'commander',
            label: '📊 Commander',
            desc: 'City-wide hospital overview and resource command',
            path: '/commander',
            color: '#8b5cf6',
        },
    ];

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            padding: '2rem',
        }}>
            {/* Logout button top-right */}
            <div style={{ position: 'fixed', top: '1.25rem', right: '1.5rem' }}>
                <button
                    onClick={handleLogout}
                    style={{
                        padding: '6px 16px',
                        background: 'transparent',
                        border: '1px solid #475569',
                        borderRadius: '8px',
                        color: '#94a3b8',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        transition: 'all 0.2s',
                    }}
                    onMouseOver={e => { e.currentTarget.style.borderColor = '#ef4444'; e.currentTarget.style.color = '#ef4444'; }}
                    onMouseOut={e => { e.currentTarget.style.borderColor = '#475569'; e.currentTarget.style.color = '#94a3b8'; }}
                >
                    Sign Out
                </button>
            </div>

            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h1 style={{
                    fontSize: '3.5rem',
                    fontWeight: 800,
                    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    marginBottom: '0.5rem',
                }}>
                    AIRA-Med
                </h1>
                <p style={{ color: '#94a3b8', fontSize: '1.125rem' }}>
                    AI-Powered Hospital Resource Monitoring
                </p>
                <p style={{ color: '#475569', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                    Welcome back. Select your dashboard to continue.
                </p>
            </div>

            {/* Role cards */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '1.5rem',
                maxWidth: '900px',
                width: '100%',
            }}>
                {roles.map(role => (
                    <div
                        key={role.id}
                        onClick={() => navigate(role.path)}
                        style={{
                            background: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '16px',
                            padding: '2rem',
                            cursor: 'pointer',
                            transition: 'all 0.25s ease',
                            textAlign: 'center',
                        }}
                        onMouseOver={e => {
                            e.currentTarget.style.borderColor = role.color;
                            e.currentTarget.style.transform = 'translateY(-6px)';
                            e.currentTarget.style.boxShadow = `0 8px 30px ${role.color}33`;
                        }}
                        onMouseOut={e => {
                            e.currentTarget.style.borderColor = '#334155';
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    >
                        <p style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>
                            {role.label.split(' ')[0]}
                        </p>
                        <h3 style={{ color: '#fff', marginBottom: '0.5rem', fontSize: '1.1rem' }}>
                            {role.label.split(' ').slice(1).join(' ')}
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.875rem', lineHeight: '1.5' }}>
                            {role.desc}
                        </p>
                        <div style={{
                            marginTop: '1.25rem',
                            display: 'inline-block',
                            padding: '6px 20px',
                            background: role.color + '22',
                            border: `1px solid ${role.color}55`,
                            borderRadius: '20px',
                            color: role.color,
                            fontSize: '0.8rem',
                            fontWeight: 600,
                        }}>
                            Open Dashboard →
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
