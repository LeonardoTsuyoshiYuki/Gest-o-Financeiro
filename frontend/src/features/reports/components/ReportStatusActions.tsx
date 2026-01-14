import React, { useState } from 'react';
import {
    IconButton, Menu, MenuItem, Dialog, DialogTitle,
    DialogContent, DialogActions, TextField, Button, ListItemIcon
} from '@mui/material';
import { MoreVert, CheckCircle, Cancel, RateReview, History } from '@mui/icons-material';
import { ReportStatus } from '../types';
import { transitionReportStatus } from '../reportService';
import { useSnackbar } from 'notistack';

interface ReportStatusActionsProps {
    reportId: number;
    currentStatus: ReportStatus;
    onStatusChange: () => void;
    onViewHistory: () => void;
}

const ReportStatusActions: React.FC<ReportStatusActionsProps> = ({ reportId, currentStatus, onStatusChange, onViewHistory }) => {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
    const [rejectComment, setRejectComment] = useState('');
    const { enqueueSnackbar } = useSnackbar();

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    const handleTransition = async (newStatus: ReportStatus, comment?: string) => {
        try {
            await transitionReportStatus(reportId, newStatus, comment);
            enqueueSnackbar('Status atualizado com sucesso.', { variant: 'success' });
            onStatusChange();
        } catch (error: any) {
            console.error("Erro na transição:", error);
            const msg = error.response?.data?.error || "Erro ao atualizar status.";
            enqueueSnackbar(msg, { variant: 'error' });
        } finally {
            handleMenuClose();
            setRejectDialogOpen(false);
            setRejectComment('');
        }
    };

    const handleRejectClick = () => {
        setRejectDialogOpen(true);
        handleMenuClose();
    };

    const submitRejection = () => {
        if (!rejectComment.trim()) {
            enqueueSnackbar('Comentário é obrigatório para rejeição.', { variant: 'warning' });
            return;
        }
        handleTransition('CANCELED', rejectComment);
    };

    // Define allowed actions based on current status
    // PENDING -> REVIEW, CANCELED
    // REVIEW -> APPROVED, CANCELED
    // FAILED -> PENDING
    const actions = [];

    if (currentStatus === 'PENDING') {
        actions.push({ label: 'Enviar para Análise', icon: <RateReview fontSize="small" />, status: 'REVIEW', handler: () => handleTransition('REVIEW') });
        actions.push({ label: 'Rejeitar / Cancelar', icon: <Cancel fontSize="small" />, status: 'CANCELED', handler: handleRejectClick });
    } else if (currentStatus === 'REVIEW') {
        actions.push({ label: 'Aprovar', icon: <CheckCircle fontSize="small" />, status: 'APPROVED', handler: () => handleTransition('APPROVED') });
        actions.push({ label: 'Rejeitar / Cancelar', icon: <Cancel fontSize="small" />, status: 'CANCELED', handler: handleRejectClick });
    } else if (currentStatus === 'FAILED') {
        actions.push({ label: 'Reiniciar Análise', icon: <RateReview fontSize="small" />, status: 'REVIEW', handler: () => handleTransition('REVIEW') });
    }

    actions.push({ label: 'Ver Histórico', icon: <History fontSize="small" />, status: 'HISTORY', handler: () => { handleMenuClose(); onViewHistory(); } });

    return (
        <>
            <IconButton size="small" onClick={handleMenuOpen}>
                <MoreVert fontSize="small" />
            </IconButton>
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
            >
                {actions.map((action) => (
                    <MenuItem key={action.label} onClick={action.handler}>
                        <ListItemIcon>{action.icon}</ListItemIcon>
                        {action.label}
                    </MenuItem>
                ))}
            </Menu>

            {/* Dialog de Rejeição */}
            <Dialog open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)}>
                <DialogTitle>Rejeitar Relatório</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Motivo da Rejeição (Obrigatório)"
                        fullWidth
                        multiline
                        rows={3}
                        value={rejectComment}
                        onChange={(e) => setRejectComment(e.target.value)}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setRejectDialogOpen(false)}>Cancelar</Button>
                    <Button onClick={submitRejection} color="error" variant="contained">Confirmar Rejeição</Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default ReportStatusActions;
