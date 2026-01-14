import { useState, useCallback } from 'react';
import { useSnackbar } from 'notistack';
import { getReports, deleteReport } from './reportsService';
import { Report, ReportFilters } from './types';

export const useReports = () => {
    const [reports, setReports] = useState<Report[]>([]);
    const [totalCount, setTotalCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const { enqueueSnackbar } = useSnackbar();

    const fetchReports = useCallback(async (filters: ReportFilters) => {
        setLoading(true);
        try {
            const data = await getReports(filters);
            setReports(data.results);
            setTotalCount(data.count);
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Erro ao carregar relatórios.', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    }, [enqueueSnackbar]);

    const removeReport = async (id: number) => {
        if (!window.confirm('Tem certeza que deseja excluir este relatório?')) return;

        try {
            await deleteReport(id);
            enqueueSnackbar('Relatório excluído com sucesso.', { variant: 'success' });
            return true;
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Falha ao excluir relatório.', { variant: 'error' });
            return false;
        }
    };

    return {
        reports,
        totalCount,
        loading,
        fetchReports,
        removeReport
    };
};
