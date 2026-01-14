import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';

interface User {
    user_id: number;
    email: string;
    role: string;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, pass: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Verificar se tem token salvo ao carregar a página
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const decoded = jwtDecode<User & { exp: number }>(token);
                // Opcional: checar expiração aqui ou deixa o interceptor lidar
                setUser(decoded);
            } catch (error) {
                console.error("Token inválido", error);
                logout();
            }
        }
        setLoading(false);
    }, []);

    const login = async (email: string, pass: string) => {
        // Axios não precisa de base URL completa se já configuramos no api.ts, 
        // mas o endpoint de auth pode ser direto via axios puro se quisermos evitar interceptors ciclicos,
        // porém aqui vou usar axios puro para login para evitar complexidade.
        const response = await api.post('/auth/token/', { email, password: pass });
        const { access, refresh } = response.data;

        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);

        const decoded = jwtDecode<User>(access);
        setUser(decoded);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
