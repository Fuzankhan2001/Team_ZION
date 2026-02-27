export default function NetworkGrid({ hospitals }) {
    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.75rem' }}>
            {hospitals?.map(h => {
                const bedPct = ((h.beds_occupied / h.beds_total) * 100).toFixed(0);
                const isStressed = bedPct >= 80;

                return (
                    <div key={h.facility_id} style={{
                        background: isStressed ? '#7f1d1d' : '#1e293b',
                        borderRadius: '8px',
                        padding: '1rem',
                        border: `1px solid ${isStressed ? '#ef4444' : '#334155'}`,
                    }}>
                        <p style={{ color: '#fff', fontWeight: 'bold', marginBottom: '4px' }}>{h.name}</p>
                        <p style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
                            Beds: {h.beds_occupied}/{h.beds_total} ({bedPct}%)
                        </p>
                        <p style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
                            O₂: {h.oxygen_percent?.toFixed(1)}% | {h.oxygen_status}
                        </p>
                    </div>
                );
            })}
        </div>
    );
}
