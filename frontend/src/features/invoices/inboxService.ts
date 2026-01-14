import api from '../../services/api';

export interface InboxItem {
    id: number;
    file_path: string | null;
    carrier: string;
    invoice_number: string | null;
    due_date: string | null;
    total_value: number;
    confidence_score: number;
    created_at: string;
    status?: 'INBOX' | 'PROCESSING' | 'OCR_RUNNING' | 'PENDING' | 'SUCCESS' | 'FAILED' | 'PENDING_REVIEW' | 'SKIPPED';
    error_message?: string;
    error_code?: string;
}

export const fetchInbox = async (): Promise<InboxItem[]> => {
    const response = await api.get('/invoices/inbox/');
    return response.data;
};

export const confirmInvoice = async (id: number, data: Partial<InboxItem>) => {
    const response = await api.post(`/invoices/${id}/confirm/`, data);
    return response.data;
};

export const downloadInvoice = async (id: number): Promise<Blob> => {
    const response = await api.get(`/invoices/${id}/download/`, { responseType: 'blob' });
    return response.data;
};
