import { useState, useEffect } from 'react';
import api from '../services/api';

export default function RealHospital() {
    const [hospital, setHospital] = useState(null);
    const facilityId = localStorage.getItem('facility_id') || 'H001';

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get(`/api/hospital/state/${facilityId}`);
                setHospital(res.data);
            } catch (err) {
                console.error('Failed:', err);
            }
        };
        fetchData();
        const interval = setInterval(fetchData, 3000);
        return () => clearInterval(interval);
    }, [facilityId]);

    if (!hospital) return <div style={{ minHeight: '100vh', background: '#0f172a', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading...</div>;

    return (
        <div style={{ minHeight: '100vh', background: '#0f172a', padding: '2rem', color: '#fff' }}>
            <h1 style={{ marginBottom: '1.5rem' }}>{hospital.name || facilityId}</h1>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div style={{ background: '#1e293b', borderRadius: '12px', padding: '1.5rem', textAlign: 'center' }}>
                    <p style={{ color: '#94a3b8' }}>Beds</p>
                    <p style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{hospital.beds_occupied}/{hospital.beds_total}</p>
                </div>
                <div style={{ background: '#1e293b', borderRadius: '12px', padding: '1.5rem', textAlign: 'center' }}>
                    <p style={{ color: '#94a3b8' }}>Ventilators</p>
                    <p style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{hospital.ventilators_in_use}/{hospital.ventilators_total}</p>
                </div>
                <div style={{ background: '#1e293b', borderRadius: '12px', padding: '1.5rem', textAlign: 'center' }}>
                    <p style={{ color: '#94a3b8' }}>Oxygen</p>
                    <p style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{hospital.oxygen_percent?.toFixed(1)}%</p>
                </div>
            </div>
        </div>
    );
}
