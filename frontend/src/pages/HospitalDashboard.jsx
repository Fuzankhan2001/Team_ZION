import { useState, useEffect } from 'react';
import api from '../services/api';
import ResourceGrid from '../components/ResourceGrid';

export default function HospitalDashboard() {
    const [hospitals, setHospitals] = useState([]);
    const [loading, setLoading] = useState(true);
    const facilityId = localStorage.getItem('facility_id');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/api/hospital/dashboard');
                setHospitals(res.data);
            } catch (err) {
                console.error('Failed to fetch dashboard:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    const myHospital = hospitals.find(h => h.facility_id === facilityId);

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#0f172a', color: '#fff' }}>
                <p>Loading dashboard...</p>
            </div>
        );
    }

    return (
        <div style={{ minHeight: '100vh', background: '#0f172a', padding: '2rem' }}>
            <h1 style={{ color: '#fff', marginBottom: '1.5rem' }}>
                Hospital Dashboard — {myHospital?.name || facilityId}
            </h1>

            {myHospital && <ResourceGrid hospital={myHospital} />}

            <h2 style={{ color: '#94a3b8', marginTop: '2rem', marginBottom: '1rem' }}>All Hospitals</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
                {hospitals.map(h => (
                    <div key={h.facility_id} style={{ background: '#1e293b', borderRadius: '12px', padding: '1.5rem' }}>
                        <h3 style={{ color: '#fff', marginBottom: '0.5rem' }}>{h.name}</h3>
                        <p style={{ color: '#94a3b8' }}>
                            Beds: {h.beds_occupied}/{h.beds_total} |
                            Vents: {h.ventilators_in_use}/{h.ventilators_total} |
                            O₂: {h.oxygen_percent?.toFixed(1)}%
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}
