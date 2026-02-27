import { useState, useEffect } from 'react';
import api from '../services/api';

export default function CommanderDashboard() {
    const [hospitals, setHospitals] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/api/hospital/dashboard');
                setHospitals(res.data);
            } catch (err) {
                console.error('Failed to fetch:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (h) => {
        const bedRatio = h.beds_occupied / h.beds_total;
        if (bedRatio >= 0.9) return '#ef4444';
        if (bedRatio >= 0.7) return '#f59e0b';
        return '#22c55e';
    };

    if (loading) return <div style={{ minHeight: '100vh', background: '#0f172a', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading...</div>;

    return (
        <div style={{ minHeight: '100vh', background: '#0f172a', padding: '2rem', color: '#fff' }}>
            <h1 style={{ marginBottom: '0.5rem' }}>📊 Commander Dashboard</h1>
            <p style={{ color: '#94a3b8', marginBottom: '2rem' }}>City-wide Hospital Overview — {hospitals.length} facilities</p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
                {hospitals.map(h => (
                    <div key={h.facility_id} style={{
                        background: '#1e293b',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        borderLeft: `4px solid ${getStatusColor(h)}`,
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h3>{h.name}</h3>
                            <span style={{ background: getStatusColor(h), padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
                                {h.city}
                            </span>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', textAlign: 'center' }}>
                            <div>
                                <p style={{ color: '#94a3b8', fontSize: '0.75rem' }}>Beds</p>
                                <p style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{h.beds_occupied}/{h.beds_total}</p>
                            </div>
                            <div>
                                <p style={{ color: '#94a3b8', fontSize: '0.75rem' }}>Vents</p>
                                <p style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{h.ventilators_in_use}/{h.ventilators_total}</p>
                            </div>
                            <div>
                                <p style={{ color: '#94a3b8', fontSize: '0.75rem' }}>O₂</p>
                                <p style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{h.oxygen_percent?.toFixed(0)}%</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
