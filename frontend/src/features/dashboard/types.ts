export interface DashboardSummary {
    total_reports: number;
    total_value: number;
    average_value: number;
    by_status: { status: string; count: number }[];
}

export interface ChartDataCategory {
    category__name: string;
    value: number;
}

export interface ChartDataTime {
    month: string;
    value: number;
}

export interface DashboardCharts {
    by_category: ChartDataCategory[];
    over_time: ChartDataTime[];
}
