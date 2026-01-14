import React from 'react';
import { Grid, Paper, Typography, Box, CircularProgress } from '@mui/material';
import { StatusSummary } from '../dashboardService';
import { AccessTime, CheckCircle, Warning, Error as ErrorIcon } from '@mui/icons-material';

interface DashboardStatsProps {
    summary: StatusSummary | null;
    loading: boolean;
}

const StatCard: React.FC<{
    title: string;
    value: string | number;
    subtitle?: string;
    icon: React.ReactNode;
    color: string;
}> = ({ title, value, subtitle, icon, color }) => (
    <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography color="textSecondary" variant="subtitle2" fontWeight="bold">
                {title.toUpperCase()}
            </Typography>
            <Box sx={{ p: 1, borderRadius: 2, bgcolor: `${color}20`, color: color }}>
                {icon}
            </Box>
        </Box>
        <Typography variant="h4" fontWeight="bold">{value}</Typography>
        {subtitle && (
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {subtitle}
            </Typography>
        )}
    </Paper>
);

const DashboardStats: React.FC<DashboardStatsProps> = ({ summary, loading }) => {
    if (loading || !summary) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}><CircularProgress /></Box>;
    }

    // Pendente (PENDING + PENDING_REVIEW potentially, but summary uses literal keys)
    const pending = summary.PENDING || { count: 0, total: 0 };
    // Aprovado
    const approved = summary.APPROVED || { count: 0, total: 0 };
    // Falha (Failed validation or process?)
    const failed = summary.FAILED || { count: 0, total: 0 };
    // Atrasados
    const overdue = summary.OVERDUE || { count: 0, total: 0 };

    const formatCurrency = (val: number) => val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    return (
        <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
                <StatCard
                    title="Pendentes"
                    value={pending.count}
                    subtitle={`Total: ${formatCurrency(pending.total)}`}
                    icon={<AccessTime />}
                    color="#f1c40f" // Warning color
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <StatCard
                    title="Aprovados"
                    value={approved.count}
                    subtitle={`Total: ${formatCurrency(approved.total)}`}
                    icon={<CheckCircle />}
                    color="#2ecc71" // Success
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <StatCard
                    title="Em Atraso"
                    value={overdue.count}
                    subtitle={`Total: ${formatCurrency(overdue.total)}`}
                    icon={<Warning />}
                    color="#e67e22" // Orange
                />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
                <StatCard
                    title="Falhas / Cancelados"
                    value={failed.count}
                    subtitle={`Total: ${formatCurrency(failed.total)}`}
                    icon={<ErrorIcon />}
                    color="#e74c3c" // Red
                />
            </Grid>
        </Grid>
    );
};

export default DashboardStats;
