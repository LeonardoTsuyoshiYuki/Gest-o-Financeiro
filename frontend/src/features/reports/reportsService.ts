import api from '../../services/api';
import { PaginatedResponse, Report, ReportFilters, Category } from './types';

export const getReports = async (filters: ReportFilters) => {
    const params = new URLSearchParams();

    if (filters.page) params.append('page', filters.page.toString());
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.status) params.append('status', filters.status);
    if (filters.category) params.append('category', filters.category.toString());

    const response = await api.get<PaginatedResponse<Report>>(`/reports/?${params.toString()}`);
    return response.data;
};

export const getCategories = async () => {
    const response = await api.get<PaginatedResponse<Category>>('/categories/');
    return response.data.results; // Assumindo paginação padrao ou endpoint sem paginação se ajustado
};


export const getReportById = async (id: number) => {
    const response = await api.get<Report>(`/reports/${id}/`);
    return response.data;
};

export const createReport = async (data: Partial<Report>) => {
    const response = await api.post<Report>('/reports/', data);
    return response.data;
};

export const updateReport = async (id: number, data: Partial<Report>) => {
    const response = await api.patch<Report>(`/reports/${id}/`, data);
    return response.data;
};

export const deleteReport = async (id: number) => {
    await api.delete(`/reports/${id}/`);
};
