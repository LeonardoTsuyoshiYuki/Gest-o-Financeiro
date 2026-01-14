import React, { useState, useEffect } from 'react';
import {
    Grid, TextField, FormControl, InputLabel, Select, MenuItem, Box
} from '@mui/material';
import { getCategories } from "../reportsService";
import { Category, ReportFilters, ReportStatus } from '../types';

interface FiltersProps {
    filters: ReportFilters;
    onFilterChange: (newFilters: Partial<ReportFilters>) => void;
}

const ReportsFilters: React.FC<FiltersProps> = ({ filters, onFilterChange }) => {
    const [categories, setCategories] = useState<Category[]>([]);

    useEffect(() => {
        getCategories().then(setCategories).catch(console.error);
    }, []);

    const handleChange = (field: keyof ReportFilters, value: any) => {
        onFilterChange({ [field]: value, page: 1 }); // Reseta para pagina 1 ao filtrar
    };

    return (
        <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={3}>
                    <TextField
                        fullWidth
                        label="Data Início"
                        type="date"
                        InputLabelProps={{ shrink: true }}
                        value={filters.start_date || ''}
                        onChange={(e) => handleChange('start_date', e.target.value)}
                        size="small"
                    />
                </Grid>
                <Grid item xs={12} sm={3}>
                    <TextField
                        fullWidth
                        label="Data Fim"
                        type="date"
                        InputLabelProps={{ shrink: true }}
                        value={filters.end_date || ''}
                        onChange={(e) => handleChange('end_date', e.target.value)}
                        size="small"
                    />
                </Grid>
                <Grid item xs={12} sm={3}>
                    <FormControl fullWidth size="small">
                        <InputLabel>Status</InputLabel>
                        <Select
                            value={filters.status || ''}
                            label="Status"
                            onChange={(e) => handleChange('status', e.target.value as ReportStatus)}
                        >
                            <MenuItem value="">Todos</MenuItem>
                            <MenuItem value="PENDING">Pendente</MenuItem>
                            <MenuItem value="APPROVED">Aprovado</MenuItem>
                            <MenuItem value="CANCELED">Cancelado</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} sm={3}>
                    <FormControl fullWidth size="small">
                        <InputLabel>Categoria</InputLabel>
                        <Select
                            value={filters.category || ''}
                            label="Categoria"
                            onChange={(e) => handleChange('category', e.target.value)}
                        >
                            <MenuItem value="">Todas</MenuItem>
                            {categories.map(cat => (
                                <MenuItem key={cat.id} value={cat.id}>
                                    {cat.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>
        </Box>
    );
};

export default ReportsFilters;
