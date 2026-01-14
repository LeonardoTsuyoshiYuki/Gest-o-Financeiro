import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import InvoiceUpload from './InvoiceUpload';
import api from '../../services/api';

// Mock do axios (via services/api)
vi.mock('../../services/api', () => ({
    default: {
        post: vi.fn()
    }
}));

// Mock do useNavigate e useSnackbar
const navigateMock = vi.fn();
const enqueueSnackbarMock = vi.fn();

vi.mock('react-router-dom', () => ({
    useNavigate: () => navigateMock
}));

vi.mock('notistack', () => ({
    useSnackbar: () => ({ enqueueSnackbar: enqueueSnackbarMock })
}));

describe('InvoiceUpload Component', () => {
    beforeEach(() => {
        vi.resetAllMocks();
    });

    it('deve renderizar o título e área de upload', () => {
        render(<InvoiceUpload />);
        expect(screen.getByText('Importar Fatura PDF')).toBeInTheDocument();
        expect(screen.getByText(/Clique aqui ou arraste o PDF/i)).toBeInTheDocument();
    });

    it('deve mostrar erro ao selecionar arquivo não PDF', async () => {
        const { container } = render(<InvoiceUpload />);
        const input = container.querySelector('input[type="file"]') as HTMLInputElement;

        const file = new File(['foo'], 'test.txt', { type: 'text/plain' });
        fireEvent.change(input, { target: { files: [file] } });

        expect(screen.getByText(/selecione apenas arquivos PDF/i)).toBeInTheDocument();
    });

    it('deve realizar upload com sucesso e redirecionar', async () => {
        (api.post as any).mockResolvedValue({
            data: { status: 'SUCCESS', message: 'Importado com sucesso' }
        });

        const { container } = render(<InvoiceUpload />);
        const input = container.querySelector('input[type="file"]') as HTMLInputElement;

        const file = new File(['%PDF-1.4'], 'fatura.pdf', { type: 'application/pdf' });
        fireEvent.change(input, { target: { files: [file] } });

        const uploadButton = screen.getByRole('button', { name: /Iniciar Importação/i });
        fireEvent.click(uploadButton);

        await waitFor(() => {
            expect(api.post).toHaveBeenCalled();
            expect(enqueueSnackbarMock).toHaveBeenCalledWith('Importado com sucesso', expect.objectContaining({ variant: 'success' }));
            expect(navigateMock).toHaveBeenCalledWith('/invoices/inbox');
        });
    });

    it('deve mostrar mensagem e redirecionar quando a API retornar SKIPPED', async () => {
        (api.post as any).mockResolvedValue({
            data: { status: 'SKIPPED', message: 'Fatura já importada.' }
        });

        const { container } = render(<InvoiceUpload />);
        const input = container.querySelector('input[type="file"]') as HTMLInputElement;
        const file = new File(['%PDF-1.4'], 'fatura.pdf', { type: 'application/pdf' });
        fireEvent.change(input, { target: { files: [file] } });

        fireEvent.click(screen.getByRole('button', { name: /Iniciar Importação/i }));

        await waitFor(() => {
            expect(enqueueSnackbarMock).toHaveBeenCalledWith('Fatura já importada.', expect.anything());
            expect(navigateMock).toHaveBeenCalledWith('/invoices/inbox');
        });
    });

    it('deve mostrar mensagem e redirecionar quando a API retornar PENDING_REVIEW', async () => {
        (api.post as any).mockResolvedValue({
            data: { status: 'PENDING_REVIEW', message: 'Revisão necessária' }
        });

        const { container } = render(<InvoiceUpload />);
        const input = container.querySelector('input[type="file"]') as HTMLInputElement;
        const file = new File(['%PDF-1.4'], 'fatura_incompleta.pdf', { type: 'application/pdf' });
        fireEvent.change(input, { target: { files: [file] } });

        fireEvent.click(screen.getByRole('button', { name: /Iniciar Importação/i }));

        await waitFor(() => {
            expect(enqueueSnackbarMock).toHaveBeenCalledWith('Revisão necessária', expect.objectContaining({ variant: 'warning' }));
            expect(navigateMock).toHaveBeenCalledWith('/invoices/inbox');
        });
    });
});
