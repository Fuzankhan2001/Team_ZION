export default function TriageWidget({ onSelect }) {
    const severities = [
        { value: 'CRITICAL', label: 'Critical', color: '#ef4444' },
        { value: 'SEVERE', label: 'Severe', color: '#f59e0b' },
        { value: 'MODERATE', label: 'Moderate', color: '#eab308' },
        { value: 'MILD', label: 'Mild', color: '#22c55e' },
    ];

    return (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
            {severities.map(s => (
                <button
                    key={s.value}
                    onClick={() => onSelect?.(s.value)}
                    style={{
                        padding: '8px 16px',
                        background: 'transparent',
                        border: `2px solid ${s.color}`,
                        color: s.color,
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        transition: 'all 0.2s',
                    }}
                    onMouseOver={e => { e.currentTarget.style.background = s.color; e.currentTarget.style.color = '#fff'; }}
                    onMouseOut={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = s.color; }}
                >
                    {s.label}
                </button>
            ))}
        </div>
    );
}
