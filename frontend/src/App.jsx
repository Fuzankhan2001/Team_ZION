import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Welcome from './pages/Welcome';
import Login from './pages/Login.jsx';
import HospitalDashboard from './pages/HospitalDashboard_FINAL.jsx';
import AmbulanceDashboard from './pages/AmbulanceDashboard.jsx';
import CommanderDashboard from './pages/CommanderDashboard.jsx';

/** Redirects to /login if the user has no JWT token in localStorage */
function ProtectedRoute({ children }) {
    const token = localStorage.getItem('token');
    if (!token) return <Navigate to="/login" replace />;
    return children;
}

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    {/* Public routes */}
                    <Route path="/login" element={<Login />} />

                    {/* Main landing page — protected */}
                    <Route
                        path="/"
                        element={
                            <ProtectedRoute>
                                <Welcome />
                            </ProtectedRoute>
                        }
                    />

                    {/* Dashboard routes — all protected */}
                    <Route
                        path="/hospital"
                        element={
                            <ProtectedRoute>
                                <HospitalDashboard />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/ambulance"
                        element={
                            <ProtectedRoute>
                                <AmbulanceDashboard />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/commander"
                        element={
                            <ProtectedRoute>
                                <CommanderDashboard />
                            </ProtectedRoute>
                        }
                    />

                    {/* Catch-all → home */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    );
}

export default App;
