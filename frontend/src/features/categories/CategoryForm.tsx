import React, { useEffect, useState } from 'react';
import {
    Box, Button, TextField, Typography, Paper, Grid, CircularProgress, Alert
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { createCategory, updateCategory, getCategoryById } from './categoriesService';

interface CategoryFormData {
    name: string;
    description: string;
}

const CategoryForm: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const isEditMode = !!id;
    const navigate = useNavigate();
    const { enqueueSnackbar } = useSnackbar();

    const [loading, setLoading] = useState(false);
    const [pageError, setPageError] = useState('');

    const { control, handleSubmit, setValue, formState: { errors } } = useForm<CategoryFormData>({
        defaultValues: {
            name: '',
            description: ''
        }
    });

    useEffect(() => {
        if (isEditMode) {
            const loadData = async () => {
                setLoading(true);
                try {
                    const data = await getCategoryById(Number(id));
                    setValue('name', data.name);
                    setValue('description', data.description || '');
                } catch (error) {
                    console.error(error);
                    setPageError('Erro ao carregar categoria.');
                } finally {
                    setLoading(false);
                }
            };
            loadData();
        }
    }, [id, isEditMode, setValue]);

    const onSubmit = async (data: CategoryFormData) => {
        setLoading(true);
        try {
            if (isEditMode) {
                await updateCategory(Number(id), data);
                enqueueSnackbar('Categoria atualizada com sucesso!', { variant: 'success' });
            } else {
                await createCategory(data);
                enqueueSnackbar('Categoria criada com sucesso!', { variant: 'success' });
            }
            navigate('/categories');
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Erro ao salvar categoria.', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    if (loading && isEditMode) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    return (
        <Paper elevation={3} sx={{ p: 4, maxWidth: 600, mx: 'auto' }}>
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold' }}>
                {isEditMode ? 'Editar Categoria' : 'Nova Categoria'}
            </Typography>

            {pageError && <Alert severity="error" sx={{ mb: 3 }}>{pageError}</Alert>}

            <Box component="form" onSubmit={handleSubmit(onSubmit)}>
                <Grid container spacing={3}>
                    <Grid item xs={12}>
                        <Controller
                            name="name"
                            control={control}
                            rules={{ required: 'Nome é obrigatório' }}
                            render={({ field }) => (
                                <TextField
                                    {...field}
                                    fullWidth
                                    label="Nome da Categoria"
                                    error={!!errors.name}
                                    helperText={errors.name?.message}
                                    disabled={loading}
                                />
                            )}
                        />
                    </Grid>

                    <Grid item xs={12}>
                        <Controller
                            name="description"
                            control={control}
                            render={({ field }) => (
                                <TextField
                                    {...field}
                                    fullWidth
                                    multiline
                                    rows={4}
                                    label="Descrição (Opcional)"
                                    disabled={loading}
                                />
                            )}
                        />
                    </Grid>

                    <Grid item xs={12} sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
                        <Button
                            variant="outlined"
                            onClick={() => navigate('/categories')}
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

export default CategoryForm;
