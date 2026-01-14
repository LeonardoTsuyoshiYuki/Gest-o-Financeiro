import api from '../../services/api';

export interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    role: 'ADMIN' | 'GESTOR' | 'ANALISTA' | 'VISUALIZADOR';
    is_active: boolean;
    password?: string;
}

export const fetchUsers = async (): Promise<User[]> => {
    const response = await api.get('/users/');
    return response.data;
};

export const fetchUser = async (id: number): Promise<User> => {
    const response = await api.get(`/users/${id}/`);
    return response.data;
};

export const createUser = async (data: Partial<User>): Promise<User> => {
    const response = await api.post('/users/', data);
    return response.data;
};

export const updateUser = async (id: number, data: Partial<User>): Promise<User> => {
    const response = await api.patch(`/users/${id}/`, data);
    return response.data;
};

export const deleteUser = async (id: number): Promise<void> => {
    await api.delete(`/users/${id}/`);
};
