import { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [role, setRole] = useState(localStorage.getItem('role'));

    const login = (tokenVal, roleVal) => {
        localStorage.setItem('token', tokenVal);
        localStorage.setItem('role', roleVal);
        setToken(tokenVal);
        setRole(roleVal);
    };

    const logout = () => {
        localStorage.clear();
        setToken(null);
        setRole(null);
    };

    return (
        <AuthContext.Provider value={{ token, role, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
