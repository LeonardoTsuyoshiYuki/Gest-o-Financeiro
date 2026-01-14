import React, { useEffect, useState } from 'react';
import {
    Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Button, Chip, Dialog, DialogTitle, DialogContent, DialogActions, TextField,
    IconButton, Switch, FormControlLabel, MenuItem, Grid
} from '@mui/material';
import { Add, Edit, Delete } from '@mui/icons-material';
import { fetchUsers, createUser, updateUser, deleteUser, User } from './userService';
import { useSnackbar } from 'notistack';

const UserList: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [open, setOpen] = useState(false);
    const [editingUser, setEditingUser] = useState<Partial<User>>({});
    const { enqueueSnackbar } = useSnackbar();

    const loadUsers = async () => {
        try {
            const data = await fetchUsers();
            setUsers(data);
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Falha ao carregar usuários.', { variant: 'error' });
        }
    };

    useEffect(() => {
        loadUsers();
    }, []);

    const handleOpen = (user?: User) => {
        setEditingUser(user || { role: 'VISUALIZADOR', is_active: true });
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
        setEditingUser({});
    };

    const handleSave = async () => {
        try {
            if (editingUser.id) {
                await updateUser(editingUser.id, editingUser);
                enqueueSnackbar('Usuário atualizado com sucesso!', { variant: 'success' });
            } else {
                await createUser(editingUser);
                enqueueSnackbar('Usuário criado com sucesso!', { variant: 'success' });
            }
            handleClose();
            loadUsers();
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Erro ao salvar usuário.', { variant: 'error' });
        }
    };

    const handleDelete = async (id: number) => {
        if (!window.confirm('Tem certeza que deseja desativar este usuário?')) return;
        try {
            // Usually we don't hard delete, but disable. But API has delete. Logic depends on backend view.
            // Backend View is RetrieveUpdateDestroyAPIView.
            await deleteUser(id);
            enqueueSnackbar('Usuário excluído.', { variant: 'success' });
            loadUsers();
        } catch (error) {
            console.error(error);
            enqueueSnackbar('Erro ao excluir usuário.', { variant: 'error' });
        }
    };

    const getRoleLabel = (role: string) => {
        const map: Record<string, string> = {
            'ADMIN': 'Administrador',
            'GESTOR': 'Gestor',
            'ANALISTA': 'Analista',
            'VISUALIZADOR': 'Visualizador'
        };
        return map[role] || role;
    };

    return (
        <Box p={3}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" fontWeight="bold">Gestão de Usuários</Typography>
                <Button variant="contained" startIcon={<Add />} onClick={() => handleOpen()}>
                    Novo Usuário
                </Button>
            </Box>

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Email</TableCell>
                            <TableCell>Nome</TableCell>
                            <TableCell>Função</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell align="right">Ações</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {users.map(user => (
                            <TableRow key={user.id}>
                                <TableCell>{user.email}</TableCell>
                                <TableCell>{user.first_name} {user.last_name}</TableCell>
                                <TableCell>
                                    <Chip label={getRoleLabel(user.role)} size="small" />
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={user.is_active ? "Ativo" : "Inativo"}
                                        color={user.is_active ? "success" : "default"}
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell align="right">
                                    <IconButton onClick={() => handleOpen(user)} color="primary">
                                        <Edit />
                                    </IconButton>
                                    <IconButton onClick={() => handleDelete(user.id)} color="error">
                                        <Delete />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
                <DialogTitle>{editingUser.id ? "Editar Usuário" : "Novo Usuário"}</DialogTitle>
                <DialogContent>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={12}>
                            <TextField
                                label="Email"
                                fullWidth
                                value={editingUser.email || ''}
                                onChange={(e) => setEditingUser({ ...editingUser, email: e.target.value })}
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                label="Nome"
                                fullWidth
                                value={editingUser.first_name || ''}
                                onChange={(e) => setEditingUser({ ...editingUser, first_name: e.target.value })}
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                label="Sobrenome"
                                fullWidth
                                value={editingUser.last_name || ''}
                                onChange={(e) => setEditingUser({ ...editingUser, last_name: e.target.value })}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                label="Função"
                                select
                                fullWidth
                                value={editingUser.role || 'VISUALIZADOR'}
                                onChange={(e) => setEditingUser({ ...editingUser, role: e.target.value as any })}
                            >
                                <MenuItem value="ADMIN">Administrador</MenuItem>
                                <MenuItem value="GESTOR">Gestor</MenuItem>
                                <MenuItem value="ANALISTA">Analista</MenuItem>
                                <MenuItem value="VISUALIZADOR">Visualizador</MenuItem>
                            </TextField>
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                label="Senha"
                                type="password"
                                fullWidth
                                helperText={editingUser.id ? "Deixe em branco para não alterar" : "Obrigatório para novos usuários"}
                                value={editingUser.password || ''}
                                onChange={(e) => setEditingUser({ ...editingUser, password: e.target.value })}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={editingUser.is_active ?? true}
                                        onChange={(e) => setEditingUser({ ...editingUser, is_active: e.target.checked })}
                                    />
                                }
                                label="Usuário Ativo"
                            />
                        </Grid>
                        {/* Username is required by model, but usually we map email to username or auto-generate. 
                            Let's assume we map email to username for now or ask.
                            Looking at User model, USERNAME_FIELD = 'email', REQUIRED_FIELDS = ['username'].
                            So AbstractUser still has username field.
                            We'll set username = email if not provided.
                        */}
                        <Grid item xs={12}>
                            <TextField
                                label="Username (Sistema)"
                                fullWidth
                                value={editingUser.username || ''}
                                onChange={(e) => setEditingUser({ ...editingUser, username: e.target.value })}
                            />
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancelar</Button>
                    <Button onClick={handleSave} variant="contained" color="primary">
                        Salvar
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default UserList;
