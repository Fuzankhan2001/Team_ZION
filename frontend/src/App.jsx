import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Welcome from './pages/Welcome';
import Login from './pages/Login.jsx';
import HospitalDashboard from './pages/HospitalDashboard.jsx';

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    <Route path="/" element={<Welcome />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/hospital" element={<HospitalDashboard />} />
                    <Route path="/ambulance" element={<div>Ambulance Dashboard — Coming Soon</div>} />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    );
}

export default App;
