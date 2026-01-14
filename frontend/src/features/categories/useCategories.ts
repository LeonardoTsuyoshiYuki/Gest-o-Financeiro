import { useState, useCallback } from 'react';
import { useSnackbar } from 'notistack';
import { getCategories, deleteCategory } from './categoriesService';
import { Category } from './types';

export const useCategories = () => {
    const [categories, setCategories] = useState<Category[]>([]);
    const [totalCount, setTotalCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const { enqueueSnackbar } = useSnackbar();

    const fetchCategories = useCallback(async () => {
        setLoading(true);
        try {
            const data = await getCategories();
            setCategories(data.results);
            setTotalCount(data.count);
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Erro ao carregar categorias.', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    }, [enqueueSnackbar]);

    const removeCategory = async (id: number) => {
        if (!window.confirm('Tem certeza que deseja excluir esta categoria?')) return;

        try {
            await deleteCategory(id);
            enqueueSnackbar('Categoria excluída com sucesso.', { variant: 'success' });
            return true;
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Falha ao excluir categoria.', { variant: 'error' });
            return false;
        }
    };

    return {
        categories,
        totalCount,
        loading,
        fetchCategories,
        removeCategory
    };
};
