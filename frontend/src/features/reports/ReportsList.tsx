import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    TablePagination, IconButton, Chip, Typography, Box, Button, CircularProgress, Tooltip
} from '@mui/material';
import { Edit, Delete, Add, CloudUpload, Download } from '@mui/icons-material';
import api from '../../services/api';
import { useReports } from './useReports';
import { ReportFilters, ReportStatus } from './types';
import ReportsFilters from './components/ReportsFilters';
import ReportStatusActions from './components/ReportStatusActions';
import ReportHistoryDialog from './components/ReportHistoryDialog';

const statusColors: Record<ReportStatus, "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning"> = {
    PENDING: 'warning',
    APPROVED: 'success',
    CANCELED: 'error',
    FAILED: 'error',
    REVIEW: 'info'
};

const ReportsList: React.FC = () => {
    const navigate = useNavigate();
    const { reports, totalCount, loading, fetchReports, removeReport } = useReports(); // Hooks embutidos

    // Estado local para filtros
    const [filters, setFilters] = useState<ReportFilters>({
        page: 1,
        status: '',
        category: '',
        start_date: '',
        end_date: ''
    });

    const [rowsPerPage] = useState(20); // Backend padrão 20
    const [historyOpen, setHistoryOpen] = useState(false);
    const [historyReportId, setHistoryReportId] = useState<number | null>(null);

    const handleOpenHistory = (id: number) => {
        setHistoryReportId(id);
        setHistoryOpen(true);
    };

    useEffect(() => {
        fetchReports(filters);
    }, [filters, fetchReports]);

    const handlePageChange = (_event: unknown, newPage: number) => {
        setFilters(prev => ({ ...prev, page: newPage + 1 }));
    };

    const handleFilterChange = (newFilters: Partial<ReportFilters>) => {
        setFilters(prev => ({ ...prev, ...newFilters }));
    };

    const handleDelete = async (id: number) => {
        const success = await removeReport(id);
        if (success) fetchReports(filters);
    };

    const downloadInvoice = async (invoiceId: number) => {
        try {
            const response = await api.get(`/invoices/${invoiceId}/download/`, {
                responseType: 'blob', // Important for file download
            });

            // Create blob link to download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;

            // Try to extract filename from header or default
            const contentDisposition = response.headers['content-disposition'];
            let fileName = 'fatura.pdf';
            if (contentDisposition) {
                const fileNameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (fileNameMatch && fileNameMatch.length === 2)
                    fileName = fileNameMatch[1].replace('"', '');
            }

            link.setAttribute('download', fileName);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error) {
            console.error("Erro ao baixar fatura:", error);
            alert("Erro ao baixar o arquivo. Talvez ele não exista mais no servidor.");
        }
    };

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h4" component="h1" fontWeight="bold">
                    Relatórios Gerenciais
                </Typography>
                <Box>
                    <Button
                        variant="outlined"
                        startIcon={<CloudUpload />}
                        onClick={() => navigate('/invoices/upload')}
                        sx={{ mr: 2 }}
                    >
                        Importar Fatura
                    </Button>
                    <Button
                        variant="contained"
                        startIcon={<Add />}
                        disabled={loading}
                        onClick={() => navigate('/reports/new')}
                    >
                        Novo Relatório
                    </Button>
                </Box>
            </Box>

            <ReportsFilters filters={filters} onFilterChange={handleFilterChange} />

            <Paper elevation={2}>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Título</TableCell>
                                <TableCell>Categoria</TableCell>
                                <TableCell>Data Ref.</TableCell>
                                <TableCell>Vencimento</TableCell>
                                <TableCell align="right">Valor (R$)</TableCell>
                                <TableCell align="center">Status</TableCell>
                                <TableCell align="center">Score</TableCell>
                                <TableCell align="center">Ações</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                                        <CircularProgress />
                                    </TableCell>
                                </TableRow>
                            ) : reports.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={7} align="center">
                                        Nenhum relatório encontrado.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                reports.map((row) => (
                                    <TableRow key={row.id} hover>
                                        <TableCell>{row.title}</TableCell>
                                        <TableCell>{row.category_name}</TableCell>
                                        <TableCell>
                                            {new Date(row.reference_date).toLocaleDateString('pt-BR')}
                                        </TableCell>
                                        <TableCell>
                                            {row.due_date ? new Date(row.due_date).toLocaleDateString('pt-BR') : '-'}
                                        </TableCell>
                                        <TableCell align="right">
                                            {parseFloat(row.total_value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                        </TableCell>
                                        <TableCell align="center">
                                            <Chip
                                                label={row.status_display}
                                                color={statusColors[row.status]}
                                                size="small"
                                                variant="outlined"
                                            />
                                        </TableCell>
                                        <TableCell align="center">
                                            {row.confidence_score !== undefined && row.confidence_score !== null ? (
                                                <Tooltip title={`Score de Confiabilidade: ${row.confidence_score}%`}>
                                                    <Chip
                                                        label={`${row.confidence_score}%`}
                                                        size="small"
                                                        color={
                                                            row.confidence_score === 100 ? 'success' :
                                                                row.confidence_score >= 80 ? 'info' :
                                                                    row.confidence_score >= 50 ? 'warning' : 'error'
                                                        }
                                                    />
                                                </Tooltip>
                                            ) : (
                                                <Typography variant="caption" color="text.secondary">N/A</Typography>
                                            )}
                                        </TableCell>
                                        <TableCell align="center">
                                            <ReportStatusActions
                                                reportId={row.id}
                                                currentStatus={row.status}
                                                onStatusChange={() => fetchReports(filters)}
                                                onViewHistory={() => handleOpenHistory(row.id)}
                                            />
                                            <IconButton size="small" color="primary" onClick={() => navigate(`/reports/${row.id}`)} aria-label="editar">
                                                <Edit fontSize="small" />
                                            </IconButton>
                                            {row.invoice_source_id && (
                                                <IconButton
                                                    size="small"
                                                    color="secondary"
                                                    onClick={() => downloadInvoice(row.invoice_source_id!)}
                                                    title="Baixar PDF Original"
                                                >
                                                    <Download fontSize="small" />
                                                </IconButton>
                                            )}
                                            <IconButton
                                                size="small"
                                                color="error"
                                                onClick={() => handleDelete(row.id)}
                                                aria-label="excluir"
                                            >
                                                <Delete fontSize="small" />
                                            </IconButton>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
                <TablePagination
                    rowsPerPageOptions={[20]}
                    component="div"
                    count={totalCount}
                    rowsPerPage={rowsPerPage}
                    page={filters.page - 1} // MUI usa 0-based
                    onPageChange={handlePageChange}
                />
            </Paper>

            <ReportHistoryDialog
                open={historyOpen}
                onClose={() => setHistoryOpen(false)}
                reportId={historyReportId}
            />
        </Box>
    );
};

export default ReportsList;
