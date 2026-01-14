import api from './api';

export interface StatusSummary {
    APPROVED: { count: number; total: number };
    PENDING: { count: number; total: number };
    PENDING_REVIEW: { count: number; total: number };
    CANCELED: { count: number; total: number };
    FAILED: { count: number; total: number };
    REVIEW?: { count: number; total: number }; // In case backend returns 'REVIEW' key
    OVERDUE: { count: number; total: number };
}

export interface TimelineData {
    month: string;
    [status: string]: number | string; // Dynamic keys for statuses
}

export const dashboardService = {
    getStatusSummary: async (): Promise<StatusSummary> => {
        const response = await api.get('/dashboard/status-summary/');
        return response.data;
    },
    getTimeline: async (): Promise<TimelineData[]> => {
        const response = await api.get('/dashboard/timeline/');
        return response.data;
    }
};
