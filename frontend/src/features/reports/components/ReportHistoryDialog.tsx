import React from 'react';
import {
    Dialog, DialogTitle, DialogContent,
    List, ListItem, ListItemText, Typography, Divider, Box
} from '@mui/material';
import { getReportHistory } from '../reportService';

interface ReportHistoryDialogProps {
    open: boolean;
    onClose: () => void;
    reportId: number | null;
}

const ReportHistoryDialog: React.FC<ReportHistoryDialogProps> = ({ open, onClose, reportId }) => {
    const [history, setHistory] = React.useState<any[]>([]);
    const [loading, setLoading] = React.useState(false);

    React.useEffect(() => {
        if (open && reportId) {
            setLoading(true);
            getReportHistory(reportId)
                .then(data => setHistory(data))
                .catch(err => console.error(err))
                .finally(() => setLoading(false));
        }
    }, [open, reportId]);

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle>Histórico de Alterações</DialogTitle>
            <DialogContent dividers>
                {loading ? (
                    <Typography>Carregando...</Typography>
                ) : history.length === 0 ? (
                    <Typography>Nenhum histórico encontrado.</Typography>
                ) : (
                    <List>
                        {history.map((log, index) => (
                            <React.Fragment key={log.id}>
                                <ListItem alignItems="flex-start">
                                    <ListItemText
                                        primary={
                                            <Typography variant="subtitle1" fontWeight="bold">
                                                {log.action}
                                            </Typography>
                                        }
                                        secondary={
                                            <>
                                                <Typography component="span" variant="body2" color="text.primary">
                                                    {new Date(log.created_at).toLocaleString('pt-BR')} - {log.user}
                                                </Typography>
                                                {log.comment && (
                                                    <Box mt={1} p={1} bgcolor="error.light" borderRadius={1}>
                                                        <Typography variant="body2" color="error.contrastText">
                                                            <strong>Motivo:</strong> {log.comment}
                                                        </Typography>
                                                    </Box>
                                                )}
                                            </>
                                        }
                                    />
                                </ListItem>
                                {index < history.length - 1 && <Divider component="li" />}
                            </React.Fragment>
                        ))}
                    </List>
                )}
            </DialogContent>
        </Dialog>
    );
};

export default ReportHistoryDialog;
