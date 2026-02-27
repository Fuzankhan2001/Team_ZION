import { useState, useEffect } from 'react';
import api from '../services/api';

export default function AmbulanceDashboard() {
    const [severity, setSeverity] = useState('CRITICAL');
    const [resource, setResource] = useState('BED');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleRequest = async () => {
        setLoading(true);
        try {
            const res = await api.post('/api/referral/request', {
                patient_severity: severity,
                required_resource: resource,
                ambulance_lat: 18.5204,
                ambulance_lon: 73.8567,
                patient_id: `P_${Date.now()}`,
            });
            setResult(res.data);
        } catch (err) {
            console.error('Referral request failed:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ minHeight: '100vh', background: '#0f172a', padding: '2rem', color: '#fff' }}>
            <h1 style={{ marginBottom: '1.5rem' }}>🚑 Ambulance Dashboard</h1>

            <div style={{ background: '#1e293b', borderRadius: '12px', padding: '1.5rem', maxWidth: '500px', marginBottom: '2rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>Request Referral</h3>

                <label style={{ color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Severity</label>
                <select value={severity} onChange={e => setSeverity(e.target.value)}
                    style={{ width: '100%', padding: '8px', marginBottom: '12px', background: '#0f172a', color: '#fff', border: '1px solid #334155', borderRadius: '6px' }}>
                    <option value="CRITICAL">Critical</option>
                    <option value="SEVERE">Severe</option>
                    <option value="MODERATE">Moderate</option>
                    <option value="MILD">Mild</option>
                </select>

                <label style={{ color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Required Resource</label>
                <select value={resource} onChange={e => setResource(e.target.value)}
                    style={{ width: '100%', padding: '8px', marginBottom: '16px', background: '#0f172a', color: '#fff', border: '1px solid #334155', borderRadius: '6px' }}>
                    <option value="BED">Bed</option>
                    <option value="VENTILATOR">Ventilator</option>
                    <option value="OXYGEN">Oxygen</option>
                </select>

                <button onClick={handleRequest} disabled={loading}
                    style={{ width: '100%', padding: '10px', background: loading ? '#64748b' : '#ef4444', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                    {loading ? 'Requesting...' : '🚨 Request Referral'}
                </button>
            </div>

            {result && (
                <div style={{ background: '#1e293b', borderRadius: '12px', padding: '1.5rem' }}>
                    <h3 style={{ color: '#22c55e', marginBottom: '1rem' }}>✓ Referral Result</h3>
                    <p><strong>Recommended:</strong> {result.recommended?.name} ({result.recommended?.facility_id})</p>
                    <p><strong>Distance:</strong> {result.recommended?.distance_km} km</p>
                    <p><strong>Score:</strong> {result.recommended?.score}</p>
                    <p><strong>Beds Available:</strong> {result.recommended?.beds_available}</p>

                    {result.alternatives?.length > 0 && (
                        <>
                            <h4 style={{ color: '#94a3b8', marginTop: '1rem', marginBottom: '0.5rem' }}>Alternatives</h4>
                            {result.alternatives.map(alt => (
                                <p key={alt.facility_id} style={{ color: '#64748b' }}>
                                    {alt.name} — {alt.distance_km}km, Score: {alt.score}
                                </p>
                            ))}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
