import api from '../../services/api';

export interface StatusSummary {
    PENDING: { count: number; total: number };
    APPROVED: { count: number; total: number };
    FAILED: { count: number; total: number };
    OVERDUE: { count: number; total: number };
    [key: string]: { count: number; total: number };
}

export interface TimelineData {
    month: string;
    APPROVED?: number;
    PENDING?: number;
    FAILED?: number;
    [key: string]: string | number | undefined;
}

export interface CarrierSummary {
    name: string;
    count: number;
    total: number;
}

export const fetchStatusSummary = async (): Promise<StatusSummary> => {
    const response = await api.get('/dashboard/status-summary/');
    return response.data;
};

export const fetchTimelineData = async (): Promise<TimelineData[]> => {
    const response = await api.get('/dashboard/timeline/');
    return response.data;
};

export const fetchCarrierSummary = async (): Promise<CarrierSummary[]> => {
    const response = await api.get('/dashboard/carrier-summary/');
    return response.data;
};
