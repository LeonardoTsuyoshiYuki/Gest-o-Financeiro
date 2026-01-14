import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import {
    Box, Button, Typography, Paper, Alert, CircularProgress,
    LinearProgress, Card, CardContent, Stack
} from '@mui/material';
import { CloudUpload, PictureAsPdf, CheckCircle, ErrorOutline, InfoOutlined, Autorenew } from '@mui/icons-material';
import api from '../../services/api';

const InvoiceUpload: React.FC = () => {
    const navigate = useNavigate();
    const { enqueueSnackbar } = useSnackbar();
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ status: string; message: string } | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const validateAndSetFile = (selectedFile: File) => {
        if (selectedFile.type !== 'application/pdf') {
            setError('Por favor, selecione apenas arquivos PDF.');
            setFile(null);
            return;
        }
        if (selectedFile.size > 10 * 1024 * 1024) { // 10MB limit
            setError('O arquivo é muito grande. O limite é de 10MB.');
            setFile(null);
            return;
        }
        setFile(selectedFile);
        setError(null);
        setResult(null);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            validateAndSetFile(e.target.files[0]);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            validateAndSetFile(e.dataTransfer.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/invoices/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            const { status, message } = response.data;

            // Treat PENDING_REVIEW and PROCESSING as non-failures that require user attention in Inbox
            if (['SUCCESS', 'PROCESSING', 'PENDING_REVIEW', 'SKIPPED'].includes(status)) {
                enqueueSnackbar(message || 'Upload recebido. Processamento iniciado.', {
                    variant: status === 'PENDING_REVIEW' ? 'warning' : 'success'
                });
                // Redirect to Inbox for review/monitoring
                navigate('/invoices/inbox');
            } else {
                // Fallback for unexpected statuses or explicitly FAILED if not caught above
                setResult(response.data);
            }

            setFile(null);
            if (fileInputRef.current) fileInputRef.current.value = '';
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.error || 'Erro ao enviar fatura. Tente novamente.');
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (status: string, message: string = '') => {
        switch (status) {
            case 'SUCCESS':
                return message.toLowerCase().includes('reprocessada')
                    ? <Autorenew color="success" sx={{ fontSize: 40 }} />
                    : <CheckCircle color="success" sx={{ fontSize: 40 }} />;
            case 'SKIPPED': return <InfoOutlined color="info" sx={{ fontSize: 40 }} />;
            case 'PENDING_REVIEW': return <InfoOutlined color="warning" sx={{ fontSize: 40 }} />;
            case 'FAILED': return <ErrorOutline color="error" sx={{ fontSize: 40 }} />;
            default: return null;
        }
    };

    const getAlertSeverity = (status: string): "success" | "info" | "error" | "warning" => {
        switch (status) {
            case 'SUCCESS': return "success";
            case 'SKIPPED': return "info";
            case 'PENDING_REVIEW': return "warning";
            case 'FAILED': return "error";
            default: return "warning";
        }
    };

    return (
        <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight="bold" textAlign="center">
                Importar Fatura PDF
            </Typography>
            <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
                Envie sua fatura (Vivo, Claro, etc.) e o sistema extrairá os dados automaticamente.
            </Typography>

            <Paper
                elevation={isDragging ? 6 : 3}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                sx={{
                    p: 4,
                    border: '2px dashed',
                    borderColor: isDragging || file ? 'primary.main' : 'divider',
                    borderRadius: 2,
                    textAlign: 'center',
                    backgroundColor: isDragging ? 'action.hover' : 'background.paper',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': { borderColor: 'primary.light' }
                }}
                onClick={() => !loading && fileInputRef.current?.click()}
            >
                <input
                    type="file"
                    accept=".pdf"
                    hidden
                    ref={fileInputRef}
                    onChange={handleFileChange}
                />

                <Box sx={{ mb: 2, transform: isDragging ? 'scale(1.1)' : 'scale(1)', transition: 'transform 0.3s' }}>
                    <CloudUpload sx={{ fontSize: 60, color: isDragging || file ? 'primary.main' : 'text.disabled' }} />
                </Box>

                {file ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                        <PictureAsPdf color="error" />
                        <Typography variant="h6">{file.name}</Typography>
                    </Box>
                ) : (
                    <Typography variant="h6" color={isDragging ? 'primary' : 'text.secondary'}>
                        {isDragging ? 'Solte o arquivo aqui!' : 'Clique aqui ou arraste o PDF da fatura'}
                    </Typography>
                )}

                <Typography variant="caption" color="text.disabled" display="block" sx={{ mt: 1 }}>
                    Limite de 10MB. Apenas formato PDF.
                </Typography>
            </Paper>

            {error && (
                <Alert severity="error" sx={{ mt: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {result && (
                <Card sx={{ mt: 3, borderLeft: 6, borderColor: `${getAlertSeverity(result.status)}.main` }}>
                    <CardContent>
                        <Stack direction="row" spacing={2} alignItems="center">
                            {getStatusIcon(result.status, result.message)}
                            <Box>
                                <Typography variant="h6" color={`${getAlertSeverity(result.status)}.main`}>
                                    {result.status === 'SUCCESS' ?
                                        (result.message.toLowerCase().includes('reprocessada') ? 'Fatura Reprocessada!' : 'Fatura Importada!') :
                                        result.status === 'SKIPPED' ? 'Já Importado (Ativo)' :
                                            result.status === 'PENDING_REVIEW' ? 'Conferência Necessária' : 'Falha na Importação'}
                                </Typography>
                                <Typography variant="body2">{result.message}</Typography>
                            </Box>
                        </Stack>
                    </CardContent>
                </Card>
            )}

            <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Button
                    variant="contained"
                    size="large"
                    aria-label="Iniciar Importação de Fatura"
                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <CloudUpload />}
                    disabled={!file || loading}
                    onClick={(e) => {
                        e.stopPropagation();
                        handleUpload();
                    }}
                    sx={{ px: 8, py: 1.5, borderRadius: 3 }}
                >
                    {loading ? 'Processando...' : 'Iniciar Importação'}
                </Button>

                {loading && (
                    <Box sx={{ width: '100%', mt: 2 }}>
                        <LinearProgress />
                        <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                            Isso pode demorar alguns segundos se o PDF precisar de OCR...
                        </Typography>
                    </Box>
                )}
            </Box>
        </Box>
    );
};

export default InvoiceUpload;
