import React from 'react';
import { Grid, Paper, Typography, Box, Stack } from '@mui/material';
import { StatusSummary } from '../../../services/dashboardService';
import { CheckCircle, Warning, ErrorOutline, Schedule, Cancel, AssignmentTurnedIn } from '@mui/icons-material';

interface DashboardKPIsProps {
    data: StatusSummary | null;
    loading: boolean;
}

const statusConfig: any = {
    APPROVED: { label: 'Aprovados', icon: <CheckCircle sx={{ fontSize: 40 }} />, color: 'success.main' },
    PENDING: { label: 'Pendentes', icon: <Schedule sx={{ fontSize: 40 }} />, color: 'warning.main' },
    REVIEW: { label: 'Em Revisão', icon: <AssignmentTurnedIn sx={{ fontSize: 40 }} />, color: 'info.main' },
    CANCELED: { label: 'Cancelados', icon: <Cancel sx={{ fontSize: 40 }} />, color: 'text.disabled' },
    FAILED: { label: 'Falhas', icon: <ErrorOutline sx={{ fontSize: 40 }} />, color: 'error.main' },
    OVERDUE: { label: 'Em Atraso', icon: <Warning sx={{ fontSize: 40 }} />, color: 'error.dark' },
};

const KPICard: React.FC<{ title: string; count: number; total: number; icon: React.ReactNode; color: string }> = ({ title, count, total, icon, color }) => (
    <Paper elevation={2} sx={{ p: 2, height: '100%', borderLeft: 6, borderColor: color }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="h6" color="text.secondary">{title}</Typography>
            <Box sx={{ color: color }}>{icon}</Box>
        </Stack>
        <Typography variant="h4" fontWeight="bold">
            {count}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
            {total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </Typography>
    </Paper>
);

const DashboardKPIs: React.FC<DashboardKPIsProps> = ({ data, loading }) => {
    if (loading || !data) {
        return <Typography>Carregando indicadores...</Typography>; // Skeleton could be better
    }

    // Map through statuses we want to show
    const keys = ['APPROVED', 'PENDING', 'REVIEW', 'OVERDUE', 'CANCELED'];

    return (
        <Grid container spacing={3}>
            {keys.map((key) => {
                const item = data[key as keyof StatusSummary] || { count: 0, total: 0 };
                const conf = statusConfig[key] || statusConfig['PENDING'];
                return (
                    <Grid item xs={12} sm={6} md={2.4} key={key}>
                        <KPICard
                            title={conf.label}
                            count={item.count}
                            total={item.total}
                            icon={conf.icon}
                            color={conf.color}
                        />
                    </Grid>
                );
            })}
        </Grid>
    );
};

export default DashboardKPIs;
