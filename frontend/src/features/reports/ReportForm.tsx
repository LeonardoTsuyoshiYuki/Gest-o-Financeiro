import React, { useEffect, useState } from 'react';
import {
    Box, Button, TextField, MenuItem, Typography, Paper, Grid, CircularProgress, Alert
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { createReport, updateReport, getReportById, getCategories } from './reportsService';
import { Category, ReportStatus } from './types';

interface ReportFormData {
    title: string;
    reference_date: string;
    due_date: string;
    category: number;
    total_value: number;
    status: ReportStatus;
}

const ReportForm: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const isEditMode = !!id;
    const navigate = useNavigate();
    const { enqueueSnackbar } = useSnackbar();

    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(false);
    const [pageError, setPageError] = useState('');

    const { control, handleSubmit, setValue, formState: { errors } } = useForm<ReportFormData>({
        defaultValues: {
            title: '',
            reference_date: new Date().toISOString().split('T')[0],
            due_date: '',
            status: 'PENDING',
            total_value: 0
        }
    });

    useEffect(() => {
        const loadDependencies = async () => {
            try {
                const cats = await getCategories();
                setCategories(cats);

                if (isEditMode) {
                    setLoading(true);
                    const report = await getReportById(Number(id));
                    setValue('title', report.title);
                    setValue('reference_date', report.reference_date);
                    setValue('due_date', report.due_date || '');
                    setValue('category', report.category);
                    setValue('total_value', parseFloat(report.total_value));
                    setValue('status', report.status);
                }
            } catch (error) {
                console.error(error);
                setPageError('Falha ao carregar dados. Tente novamente.');
            } finally {
                setLoading(false);
            }
        };
        loadDependencies();
    }, [id, isEditMode, setValue]);

    const onSubmit = async (data: ReportFormData) => {
        setLoading(true);
        try {
            // Convert form data to API format (total_value must be string)
            const payload = {
                ...data,
                total_value: data.total_value.toString()
            };

            if (isEditMode) {
                await updateReport(Number(id), payload);
                enqueueSnackbar('Relatório atualizado com sucesso!', { variant: 'success' });
            } else {
                await createReport(payload);
                enqueueSnackbar('Relatório criado com sucesso!', { variant: 'success' });
            }
            navigate('/reports');
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Erro ao salvar relatório.', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    if (loading && isEditMode && !categories.length) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    return (
        <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold' }}>
                {isEditMode ? 'Editar Relatório' : 'Novo Relatório'}
            </Typography>

            {pageError && <Alert severity="error" sx={{ mb: 3 }}>{pageError}</Alert>}

            <Box component="form" onSubmit={handleSubmit(onSubmit)}>
                <Grid container spacing={3}>
                    <Grid item xs={12}>
                        <Controller
                            name="title"
                            control={control}
                            rules={{ required: 'Título é obrigatório' }}
                            render={({ field }) => (
                                <TextField
                                    {...field}
                                    fullWidth
                                    label="Título"
                                    error={!!errors.title}
                                    helperText={errors.title?.message}
                                    disabled={loading}
                                />
                            )}
                        />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                        <Controller
                            name="category"
                            control={control}
                            rules={{ required: 'Categoria é obrigatória' }}
                            render={({ field }) => (
                                <TextField
                                    {...field}
                                    select
                                    fullWidth
                                    label="Categoria"
                                    error={!!errors.category}
                                    helperText={errors.category?.message}
                                    disabled={loading}
                                >
                                    {categories.map((cat) => (
                                        <MenuItem key={cat.id} value={cat.id}>
                                            {cat.name}
                                        </MenuItem>
                                    ))}
                                </TextField>
                            )}
                        />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                        <Controller
                            name="status"
                            control={control}
                            render={({ field }) => (
                                <TextField
                                    {...field}
                                    select
                                    fullWidth
                                    label="Status"
                                    disabled={loading}
                                >
                                    <MenuItem value="PENDING">Pendente</MenuItem>
                                    <MenuItem value="APPROVED">Aprovado</MenuItem>
                                    <MenuItem value="CANCELED">Cancelado</MenuItem>
                                    <MenuItem value="FAILED">Falha</MenuItem>
                                    <MenuItem value="REVIEW">Aguardando Revisão</MenuItem>
                                </TextField>
                            )}
                        />
                    </Grid>

                    <Grid item xs={12} sm={4}>
                        <Controller
                            name="reference_date"
                            control={control}
                            rules={{ required: 'Data é obrigatória' }}
                            render={({ field }) => (
                                <TextField
                                    {...field}
                                    type="date"
                                    fullWidth
                                    label="Data de Referência"
                                    InputLabelProps={{ shrink: true }}
                                    error={!!errors.reference_date}
                                    helperText={errors.reference_date?.message}
                                    disabled={loading}
                                />
                            )}
                        />
                    </Grid>

                    <Grid item xs={12} sm={4}>
                        <Controller
                            name="due_date"
                            control={control}
                            render={({ field }) => (
                                <TextField
                                    {...field}
                                    type="date"
                                    fullWidth
                                    label="Data de Vencimento"
                                    InputLabelProps={{ shrink: true }}
                                    disabled={loading}
                                />
                            )}
                        />
                    </Grid>

                    <Grid item xs={12} sm={4}>
                        <Controller
                            name="total_value"
                            control={control}
                            rules={{
                                required: 'Valor é obrigatório',
                                min: { value: 0.01, message: 'Valor deve ser maior que zero' }
                            }}
                            render={({ field }) => (
                                <TextField
                                    {...field}
                                    type="number"
                                    fullWidth
                                    label="Valor Total (R$)"
                                    error={!!errors.total_value}
                                    helperText={errors.total_value?.message}
                                    disabled={loading}
                                />
                            )}
                        />
                    </Grid>

                    <Grid item xs={12} sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
                        <Button
                            variant="outlined"
                            onClick={() => navigate('/reports')}
                            disabled={loading}
                        >
                            Cancelar
                        </Button>
                        <Button
                            type="submit"
                            variant="contained"
                            disabled={loading}
                        >
                            {loading ? 'Salvando...' : 'Salvar'}
                        </Button>
                    </Grid>
                </Grid>
            </Box>
        </Paper>
    );
};

export default ReportForm;
