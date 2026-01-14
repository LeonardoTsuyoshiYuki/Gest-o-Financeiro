import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import Login from './Login';
import * as AuthContext from '../../context/AuthContext';

// Mock do useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

describe('Login Component', () => {
    const mockLogin = vi.fn();

    beforeEach(() => {
        vi.resetAllMocks();
        // Mock do Hook useAuth
        vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
            login: mockLogin,
            user: null,
            loading: false,
            logout: vi.fn(),
            isAuthenticated: false
        });
    });

    it('deve renderizar o formulário corretamente', () => {
        render(<Login />);
        expect(screen.getByText('Acesso Corporativo')).toBeInTheDocument();
        expect(screen.getByLabelText(/Endereço de Email/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Senha/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Entrar/i })).toBeInTheDocument();
    });

    it('deve permitir digitar email e senha', () => {
        render(<Login />);
        const emailInput = screen.getByLabelText(/Endereço de Email/i);
        const passInput = screen.getByLabelText(/Senha/i);

        fireEvent.change(emailInput, { target: { value: 'teste@email.com' } });
        fireEvent.change(passInput, { target: { value: 'senha123' } });

        expect(emailInput).toHaveValue('teste@email.com');
        expect(passInput).toHaveValue('senha123');
    });

    it('deve chamar a função de login e navegar ao submeter com sucesso', async () => {
        render(<Login />);
        const emailInput = screen.getByLabelText(/Endereço de Email/i);
        const passInput = screen.getByLabelText(/Senha/i);
        const submitButton = screen.getByRole('button', { name: /Entrar/i });

        fireEvent.change(emailInput, { target: { value: 'valid@email.com' } });
        fireEvent.change(passInput, { target: { value: 'password' } });

        fireEvent.click(submitButton);

        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalledWith('valid@email.com', 'password');
        });
        expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    it('deve exibir mensagem de erro se o login falhar', async () => {
        mockLogin.mockRejectedValue(new Error('Auth failed'));

        render(<Login />);
        const emailInput = screen.getByLabelText(/Endereço de Email/i);
        const passInput = screen.getByLabelText(/Senha/i);
        const submitButton = screen.getByRole('button', { name: /Entrar/i });

        fireEvent.change(emailInput, { target: { value: 'test@email.com' } });
        fireEvent.change(passInput, { target: { value: 'password' } });

        fireEvent.click(submitButton);

        await waitFor(() => {
            expect(screen.getByText(/Falha no login/i)).toBeInTheDocument();
        });
    });

    it('deve desabilitar botão enquanto carrega', async () => {
        // Simula delay no login
        mockLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

        render(<Login />);
        const emailInput = screen.getByLabelText(/Endereço de Email/i);
        const passInput = screen.getByLabelText(/Senha/i);
        const submitButton = screen.getByRole('button', { name: /Entrar/i });

        fireEvent.change(emailInput, { target: { value: 'test@email.com' } });
        fireEvent.change(passInput, { target: { value: 'password' } });

        fireEvent.click(submitButton);

        expect(submitButton).toBeDisabled();
        expect(screen.getByText('Entrando...')).toBeInTheDocument();

        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalled();
        });
    });
});
