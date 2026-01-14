import api from '../../services/api';
import { Category, PaginatedResponse } from './types';

export const getCategories = async () => {
    // Assuming the API returns paginated response, but for categories usually we might want all or paginated. 
    // The previous implementation in reportsService used /categories/ which returns PaginatedResponse.
    const response = await api.get<PaginatedResponse<Category>>('/categories/');
    return response.data;
};

export const getCategoryById = async (id: number) => {
    const response = await api.get<Category>(`/categories/${id}/`);
    return response.data;
};

export const createCategory = async (data: Partial<Category>) => {
    const response = await api.post<Category>('/categories/', data);
    return response.data;
};

export const updateCategory = async (id: number, data: Partial<Category>) => {
    const response = await api.patch<Category>(`/categories/${id}/`, data);
    return response.data;
};

export const deleteCategory = async (id: number) => {
    await api.delete(`/categories/${id}/`);
};
