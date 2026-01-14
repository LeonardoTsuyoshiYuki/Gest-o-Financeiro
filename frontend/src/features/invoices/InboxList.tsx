import React, { useEffect, useState } from 'react';
import {
    Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Button, Chip, Tooltip, Dialog, DialogTitle, DialogContent,
    DialogActions, TextField, Grid, CircularProgress, Alert, IconButton
} from '@mui/material';
import { CheckCircle, Warning, Download } from '@mui/icons-material';
import { fetchInbox, confirmInvoice, downloadInvoice, InboxItem } from './inboxService';
import { useSnackbar } from 'notistack';

const InboxList: React.FC = () => {
    const [items, setItems] = useState<InboxItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [reviewItem, setReviewItem] = useState<InboxItem | null>(null);
    const [reviewData, setReviewData] = useState<Partial<InboxItem>>({});
    const { enqueueSnackbar } = useSnackbar();

    const loadData = async (silent = false) => {
        if (!silent) setLoading(true);
        try {
            const data = await fetchInbox();
            setItems(data);
        } catch (error) {
            console.error(error);
            if (!silent) enqueueSnackbar('Falha ao carregar inbox.', { variant: 'error' });
        } finally {
            if (!silent) setLoading(false);
        }
    };

    useEffect(() => {
        loadData();

        // Polling every 5 seconds to check for status updates (e.g. PROCESSING -> SUCCESS)
        const interval = setInterval(() => {
            loadData(true);
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    const handleOpenReview = (item: InboxItem) => {
        setReviewItem(item);
        setReviewData({
            total_value: item.total_value,
            due_date: item.due_date ? item.due_date : '',
            invoice_number: item.invoice_number,
            carrier: item.carrier
        });
    };

    const handleConfirm = async () => {
        if (!reviewItem) return;
        try {
            await confirmInvoice(reviewItem.id, reviewData);
            enqueueSnackbar('Fatura confirmada com sucesso!', { variant: 'success' });
            setReviewItem(null);
            loadData();
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Erro ao confirmar fatura.', { variant: 'error' });
        }
    };

    const handleDownload = async (item: InboxItem) => {
        try {
            const blob = await downloadInvoice(item.id);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `fatura_${item.id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            enqueueSnackbar('Download iniciado.', { variant: 'success' });
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Erro ao baixar arquivo. Verifique permissões.', { variant: 'error' });
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'success';
        if (score >= 50) return 'warning';
        return 'error';
    };

    return (
        <Box>
            <Typography variant="h4" gutterBottom fontWeight="bold">Caixa de Entrada (Revisão)</Typography>

            {items.length === 0 && !loading && (
                <Alert severity="info">Nenhuma fatura pendente de revisão.</Alert>
            )}

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Data Importação</TableCell>
                            <TableCell>Operadora</TableCell>
                            <TableCell>Valor Extraído</TableCell>
                            <TableCell align="center">Score</TableCell>
                            <TableCell align="center">Ação</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {loading && (
                            <TableRow>
                                <TableCell colSpan={5} align="center"><CircularProgress /></TableCell>
                            </TableRow>
                        )}
                        {!loading && items.map(item => (
                            <TableRow key={item.id} hover>
                                <TableCell>{new Date(item.created_at).toLocaleString('pt-BR')}</TableCell>
                                <TableCell>{item.carrier}</TableCell>
                                <TableCell>{item.total_value?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</TableCell>
                                <TableCell align="center">
                                    {item.status === 'PROCESSING' || item.status === 'OCR_RUNNING' ? (
                                        <Chip label="Processando..." color="info" size="small" icon={<CircularProgress size={16} />} />
                                    ) : item.status === 'FAILED' ? (
                                        <Tooltip title={
                                            <React.Fragment>
                                                <Typography color="inherit" variant="subtitle2">Falha na Importação</Typography>
                                                <b>Erro:</b> {item.error_message || "N/A"}<br />
                                                <b>Código:</b> {item.error_code || "UNKNOWN"}
                                            </React.Fragment>
                                        }>
                                            <Chip label="Falha" color="error" size="small" icon={<Warning />} />
                                        </Tooltip>
                                    ) : item.status === 'SKIPPED' ? (
                                        <Tooltip title="Arquivo duplicado e já processado anteriormente.">
                                            <Chip label="Duplicado" color="default" size="small" />
                                        </Tooltip>
                                    ) : (
                                        <Tooltip title={`${item.confidence_score}% de confiança`}>
                                            <Chip
                                                label={`${item.confidence_score}%`}
                                                color={getScoreColor(item.confidence_score)}
                                                size="small"
                                            />
                                        </Tooltip>
                                    )}
                                </TableCell>
                                <TableCell align="center">
                                    {['INBOX', 'PENDING_REVIEW'].includes(item.status || '') ? (
                                        <Box display="flex" justifyContent="center" alignItems="center">
                                            <Tooltip title="Exportar PDF">
                                                <IconButton
                                                    onClick={() => handleDownload(item)}
                                                    size="small"
                                                    color="primary"
                                                    aria-label="Exportar PDF"
                                                    sx={{ mr: 1 }}
                                                >
                                                    <Download fontSize="small" />
                                                </IconButton>
                                            </Tooltip>
                                            <Button
                                                variant="contained"
                                                size="small"
                                                startIcon={<CheckCircle />}
                                                aria-label={`Revisar fatura ${item.invoice_number || 'Sem número'}`}
                                                onClick={() => handleOpenReview(item)}
                                            >
                                                Revisar
                                            </Button>
                                        </Box>
                                    ) : (
                                        <Typography variant="caption" color="text.secondary">
                                            {item.status === 'FAILED' ? (item.error_message || 'Erro no processamento') : 'Aguarde...'}
                                        </Typography>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            {/* Dialog de Revisão */}
            <Dialog open={!!reviewItem} onClose={() => setReviewItem(null)} maxWidth="md" fullWidth>
                <DialogTitle>Revisar Fatura</DialogTitle>
                <DialogContent>

                    {reviewItem && (
                        <Grid container spacing={2} sx={{ mt: 1 }}>
                            <Grid item xs={12} md={6}>
                                <Typography variant="subtitle1" gutterBottom>Pré-visualização</Typography>
                                <Box sx={{ border: '1px solid #ccc', height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f5' }}>
                                    {reviewItem.file_path ? (
                                        <Typography>PDF disponível (Mock)</Typography>
                                        // Em produção, usar um PDF viewer ou iframe
                                    ) : (
                                        <Typography color="error">Arquivo não disponível</Typography>
                                    )}
                                </Box>
                                <Button
                                    sx={{ mt: 1 }}
                                    onClick={() => handleDownload(reviewItem)}
                                    variant="outlined"
                                    fullWidth
                                    startIcon={<Download />}
                                >
                                    Exportar PDF Seguro
                                </Button>
                            </Grid>

                            <Grid item xs={12} md={6}>
                                <Typography variant="subtitle1" gutterBottom>Dados Extraídos</Typography>
                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                    <TextField
                                        label="Operadora"
                                        value={reviewData.carrier}
                                        onChange={(e) => setReviewData({ ...reviewData, carrier: e.target.value })}
                                        fullWidth
                                    />
                                    <TextField
                                        label="Número da Fatura"
                                        value={reviewData.invoice_number || ''}
                                        onChange={(e) => setReviewData({ ...reviewData, invoice_number: e.target.value })}
                                        fullWidth
                                    />
                                    <TextField
                                        label="Valor Total (R$)"
                                        type="number"
                                        value={reviewData.total_value}
                                        onChange={(e) => setReviewData({ ...reviewData, total_value: parseFloat(e.target.value) })}
                                        fullWidth
                                        error={reviewData.total_value === 0}
                                        helperText={reviewData.total_value === 0 ? "Valor zerado exige atenção" : ""}
                                    />
                                    <TextField
                                        label="Vencimento"
                                        type="date"
                                        InputLabelProps={{ shrink: true }}
                                        value={reviewData.due_date}
                                        onChange={(e) => setReviewData({ ...reviewData, due_date: e.target.value })}
                                        fullWidth
                                    />

                                    {reviewItem.confidence_score < 50 && (
                                        <Alert severity="warning" icon={<Warning />}>
                                            Atenção: A extração automática teve baixa confiança. Por favor verifique cuidadosamente os dados.
                                        </Alert>
                                    )}
                                </Box>
                            </Grid>
                        </Grid>
                    )}

                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setReviewItem(null)}>Cancelar</Button>
                    <Button onClick={handleConfirm} variant="contained" color="success">
                        Confirmar e Gerar Relatório
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default InboxList;
