import React from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    LineChart, Line
} from 'recharts';
import { TimelineData, CarrierSummary } from '../dashboardService';

import { useTheme } from '@mui/material/styles';

interface DashboardChartsProps {
    timeline: TimelineData[];
    carriers: CarrierSummary[];
}

const DashboardCharts: React.FC<DashboardChartsProps> = ({ timeline, carriers }) => {
    const theme = useTheme();

    // Limits
    const topCarriers = carriers.slice(0, 10);

    // Theme adaptions
    const isDark = theme.palette.mode === 'dark';
    const gridColor = isDark ? '#374151' : '#e5e7eb';
    const textColor = theme.palette.text.secondary;

    const tooltipStyle = {
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
        color: theme.palette.text.primary
    };

    return (
        <Grid container spacing={3} sx={{ mt: 1 }}>
            {/* Evolução Temporal */}
            <Grid item xs={12} md={8}>
                <Paper sx={{ p: 2, height: 400 }}>
                    <Typography variant="h6" gutterBottom>Evolução de Custos (Mensal)</Typography>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={timeline}>
                            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                            <XAxis
                                dataKey="month"
                                tickFormatter={(v) => v.slice(0, 7)}
                                stroke={textColor}
                                tick={{ fill: textColor }}
                            />
                            <YAxis
                                tickFormatter={(val) => `R$${val / 1000}k`}
                                stroke={textColor}
                                tick={{ fill: textColor }}
                            />
                            <Tooltip
                                formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                contentStyle={tooltipStyle}
                                cursor={{ stroke: textColor, opacity: 0.2 }}
                            />
                            <Legend />
                            <Line type="monotone" dataKey="APPROVED" name="Aprovado" stroke="#2ecc71" strokeWidth={2} dot={{ r: 4 }} />
                            <Line type="monotone" dataKey="PENDING" name="Pendente" stroke="#f1c40f" strokeWidth={2} dot={{ r: 4 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </Paper>
            </Grid>

            {/* Top Operadoras */}
            <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2, height: 400 }}>
                    <Typography variant="h6" gutterBottom>Custos por Operadora</Typography>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart layout="vertical" data={topCarriers} margin={{ left: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                            <XAxis type="number" hide />
                            <YAxis
                                dataKey="name"
                                type="category"
                                width={80}
                                stroke={textColor}
                                tick={{ fill: textColor }}
                            />
                            <Tooltip
                                formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                contentStyle={tooltipStyle}
                                cursor={{ fill: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' }}
                            />
                            <Bar dataKey="total" fill={theme.palette.primary.main} radius={[0, 4, 4, 0]} name="Total" />
                        </BarChart>
                    </ResponsiveContainer>
                </Paper>
            </Grid>
        </Grid>
    );
};

export default DashboardCharts;
