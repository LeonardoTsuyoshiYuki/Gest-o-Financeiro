import api from '../../services/api';
import { ReportStatus } from './types';

export const transitionReportStatus = async (id: number, status: ReportStatus, comment?: string) => {
    const response = await api.post(`/reports/${id}/transition/`, { status, comment });
    return response.data;
};

export const getReportHistory = async (id: number) => {
    const response = await api.get(`/reports/${id}/history/`);
    return response.data;
};
