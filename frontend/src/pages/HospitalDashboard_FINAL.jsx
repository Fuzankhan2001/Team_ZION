import { useState, useEffect } from 'react';
import api from '../services/api';
import ResourceGrid from '../components/ResourceGrid';

export default function HospitalDashboard_FINAL() {
    const [hospitals, setHospitals] = useState([]);
    const [myHospital, setMyHospital] = useState(null);
    const [loading, setLoading] = useState(true);
    const [crisisMode, setCrisisMode] = useState(false);
    const facilityId = localStorage.getItem('facility_id');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/api/hospital/dashboard');
                setHospitals(res.data);
                const mine = res.data.find(h => h.facility_id === facilityId);
                setMyHospital(mine);
            } catch (err) {
                console.error('Failed to fetch dashboard:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [facilityId]);

    const toggleCrisis = async () => {
        try {
            if (crisisMode) {
                await api.post('/api/hospital/anti-crisis');
            } else {
                await api.post('/api/hospital/crisis');
            }
            setCrisisMode(!crisisMode);
        } catch (err) {
            console.error('Crisis toggle failed:', err);
        }
    };

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#0f172a', color: '#fff' }}>
                <p>Loading dashboard...</p>
            </div>
        );
    }

    return (
        <div style={{ minHeight: '100vh', background: crisisMode ? '#1a0000' : '#0f172a', padding: '2rem', transition: 'background 0.5s' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h1 style={{ color: '#fff' }}>
                    Hospital Dashboard — {myHospital?.name || facilityId}
                </h1>
                <button
                    onClick={toggleCrisis}
                    style={{
                        padding: '8px 20px',
                        background: crisisMode ? '#22c55e' : '#ef4444',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        fontSize: '0.875rem',
                    }}
                >
                    {crisisMode ? '✓ Deactivate Crisis' : '⚠ Activate Crisis Mode'}
                </button>
            </div>

            {myHospital && <ResourceGrid hospital={myHospital} />}

            <h2 style={{ color: '#94a3b8', marginTop: '2rem', marginBottom: '1rem' }}>Network Hospitals</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
                {hospitals.map(h => {
                    const bedPct = h.beds_total > 0 ? (h.beds_occupied / h.beds_total * 100).toFixed(0) : 0;
                    const isStressed = bedPct >= 80;

                    return (
                        <div key={h.facility_id} style={{
                            background: isStressed ? '#7f1d1d' : '#1e293b',
                            borderRadius: '12px',
                            padding: '1.5rem',
                            border: `1px solid ${isStressed ? '#ef4444' : '#334155'}`,
                        }}>
                            <h3 style={{ color: '#fff', marginBottom: '0.5rem' }}>{h.name}</h3>
                            <p style={{ color: '#94a3b8' }}>
                                Beds: {h.beds_occupied}/{h.beds_total} ({bedPct}%) |
                                Vents: {h.ventilators_in_use}/{h.ventilators_total} |
                                O₂: {h.oxygen_percent?.toFixed(1)}%
                            </p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
