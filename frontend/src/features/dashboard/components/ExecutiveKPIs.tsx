import React from 'react';
import { Grid, Paper, Typography, Box, Stack, Divider, Alert } from '@mui/material';
import { TrendingUp, TrendingDown, Error as ErrorIcon, AttachMoney, ContentCopy, Lightbulb } from '@mui/icons-material';
import { DashboardInsights } from '../dashboardService';

interface ExecutiveKPIsProps {
    data: DashboardInsights | null;
    loading: boolean;
}

const InsightCard: React.FC<{
    title: string;
    value: string | number;
    subtitle?: React.ReactNode;
    icon: React.ReactNode;
    color: string;
}> = ({ title, value, subtitle, icon, color }) => (
    <Paper elevation={3} sx={{ p: 3, height: '100%', position: 'relative', overflow: 'hidden' }}>
        <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.1, color: color, transform: 'scale(2.5)' }}>
            {icon}
        </Box>
        <Stack spacing={1}>
            <Typography variant="subtitle2" color="text.secondary" fontWeight="bold">
                {title.toUpperCase()}
            </Typography>
            <Typography variant="h4" fontWeight="bold" color="text.primary">
                {value}
            </Typography>
            {subtitle && (
                <Box>
                    {subtitle}
                </Box>
            )}
        </Stack>
    </Paper>
);

const ExecutiveKPIs: React.FC<ExecutiveKPIsProps> = ({ data, loading }) => {
    if (loading || !data) {
        return <Typography>Carregando painel executivo...</Typography>;
    }

    const {
        current_month_total,
        variation_percent,
        import_errors_count,
        skipped_count,
        report_count,
        insights_list
    } = data;

    const isExpenseIncrease = variation_percent > 0;
    const variationColor = isExpenseIncrease ? 'error.main' : 'success.main';
    const variationIcon = isExpenseIncrease ? <TrendingUp /> : <TrendingDown />;

    return (
        <Box mb={4}>
            <Grid container spacing={3}>
                {/* Faturamento Mês Atual */}
                <Grid item xs={12} md={4}>
                    <InsightCard
                        title="Despesas (Mês Atual)"
                        value={current_month_total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        color="primary.main"
                        icon={<AttachMoney />}
                        subtitle={
                            <Stack direction="row" alignItems="center" spacing={1} sx={{ color: variationColor }}>
                                {variationIcon}
                                <Typography variant="body2" fontWeight="bold">
                                    {Math.abs(variation_percent)}% vs mês anterior
                                </Typography>
                            </Stack>
                        }
                    />
                </Grid>

                {/* Volume de Faturas */}
                <Grid item xs={12} md={4}>
                    <InsightCard
                        title="Volume de Faturas"
                        value={report_count}
                        color="info.main"
                        icon={<ContentCopy />} // Using generic icon
                        subtitle={
                            <Typography variant="body2" color="text.secondary">
                                Processadas neste mês
                            </Typography>
                        }
                    />
                </Grid>

                {/* Qualidade da Importação */}
                <Grid item xs={12} md={4}>
                    <InsightCard
                        title="Atenção Necessária"
                        value={import_errors_count + skipped_count}
                        color={import_errors_count > 0 ? 'error.main' : 'success.main'}
                        icon={<ErrorIcon />}
                        subtitle={
                            <Stack direction="row" spacing={1}>
                                <Typography variant="caption" color="error.main">
                                    {import_errors_count} Erros
                                </Typography>
                                <Divider orientation="vertical" flexItem />
                                <Typography variant="caption" color="text.secondary">
                                    {skipped_count} Duplicadas
                                </Typography>
                            </Stack>
                        }
                    />
                </Grid>
            </Grid>

            {/* AI Insights Section */}
            {insights_list.length > 0 && (
                <Box mt={3}>
                    <Paper sx={{ p: 2, bgcolor: 'background.default', border: '1px solid', borderColor: 'divider' }}>
                        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                            <Lightbulb color="warning" />
                            <Typography variant="h6" fontWeight="bold">Insights Automáticos</Typography>
                        </Stack>
                        <Stack spacing={1}>
                            {insights_list.map((insight, index) => (
                                <Alert key={index} severity="info" variant="outlined" sx={{ border: 'none', bgcolor: 'white' }}>
                                    {insight}
                                </Alert>
                            ))}
                        </Stack>
                    </Paper>
                </Box>
            )}
        </Box>
    );
};

export default ExecutiveKPIs;
