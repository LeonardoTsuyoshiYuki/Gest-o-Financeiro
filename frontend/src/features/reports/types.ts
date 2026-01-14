export interface Category {
    id: number;
    name: string;
    description?: string;
}

export type ReportStatus = 'PENDING' | 'APPROVED' | 'CANCELED' | 'FAILED' | 'REVIEW';

export interface Report {
    id: number;
    title: string;
    reference_date: string;
    category: number;
    category_name?: string;
    total_value: string;
    due_date?: string;
    status: ReportStatus;
    status_display?: string;
    invoice_source_id?: number | null;
    confidence_score?: number;
    created_at: string;
}

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export interface ReportFilters {
    start_date?: string;
    end_date?: string;
    status?: ReportStatus | '';
    category?: number | '';
    page: number;
}
