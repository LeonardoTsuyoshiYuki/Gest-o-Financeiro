import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, Stack, CircularProgress } from '@mui/material';
import { Refresh } from '@mui/icons-material';
import DashboardStats from './components/DashboardStats';
import DashboardCharts from './components/DashboardCharts';
import { fetchStatusSummary, fetchTimelineData, fetchCarrierSummary, StatusSummary, TimelineData, CarrierSummary } from './dashboardService';

const Dashboard: React.FC = () => {
    const [summary, setSummary] = useState<StatusSummary | null>(null);
    const [timeline, setTimeline] = useState<TimelineData[]>([]);
    const [carriers, setCarriers] = useState<CarrierSummary[]>([]);
    const [loading, setLoading] = useState(true);

    const loadData = async () => {
        setLoading(true);
        try {
            const [sumData, timeData, carrData] = await Promise.all([
                fetchStatusSummary(),
                fetchTimelineData(),
                fetchCarrierSummary()
            ]);
            setSummary(sumData);
            setTimeline(timeData);
            setCarriers(carrData);
        } catch (error) {
            console.error("Erro ao carregar dados do dashboard", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    return (
        <Box>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={4}>
                <Typography variant="h4" fontWeight="bold">
                    Dashboard Gerencial
                </Typography>
                <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    onClick={loadData}
                >
                    Atualizar
                </Button>
            </Stack>

            {loading && !summary ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <>
                    <Box mb={4}>
                        <DashboardStats summary={summary} loading={loading} />
                    </Box>
                    <Box>
                        <DashboardCharts timeline={timeline} carriers={carriers} />
                    </Box>
                </>
            )}
        </Box>
    );
};

export default Dashboard;
