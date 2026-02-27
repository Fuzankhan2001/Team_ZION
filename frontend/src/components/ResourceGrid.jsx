export default function ResourceGrid({ hospital }) {
    const cards = [
        {
            label: 'Beds',
            used: hospital.beds_occupied,
            total: hospital.beds_total,
            color: hospital.beds_occupied / hospital.beds_total >= 0.8 ? '#ef4444' : '#22c55e',
        },
        {
            label: 'Ventilators',
            used: hospital.ventilators_in_use,
            total: hospital.ventilators_total,
            color: hospital.ventilators_in_use / hospital.ventilators_total >= 0.8 ? '#ef4444' : '#3b82f6',
        },
        {
            label: 'Oxygen',
            used: `${hospital.oxygen_percent?.toFixed(1)}%`,
            total: '100%',
            color: hospital.oxygen_percent <= 30 ? '#ef4444' : '#22c55e',
        },
    ];

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            {cards.map(card => (
                <div key={card.label} style={{
                    background: '#1e293b',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    borderLeft: `4px solid ${card.color}`,
                }}>
                    <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '0.5rem' }}>{card.label}</p>
                    <p style={{ color: '#fff', fontSize: '2rem', fontWeight: 'bold' }}>
                        {card.used} <span style={{ color: '#64748b', fontSize: '1rem' }}>/ {card.total}</span>
                    </p>
                </div>
            ))}
        </div>
    );
}
