import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import ReportsList from './ReportsList';
// Importamos o *arquivo* do hook para fazer spy
import * as useReportsHook from './useReports';

// Mock do useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

// Mock dos componentes filhos para simplificar teste
vi.mock('./components/ReportsFilters', () => ({
    default: ({ onFilterChange }: any) => (
        <div data-testid="filters">
            <button onClick={() => onFilterChange({ status: 'APPROVED' })}>Aplicar Filtro</button>
        </div>
    )
}));

describe('ReportsList Component', () => {
    // Helper para mockar o retorno do hook
    const mockUseReports = (overrides = {}) => {
        const defaultValues = {
            reports: [],
            totalCount: 0,
            loading: false,
            fetchReports: vi.fn(),
            removeReport: vi.fn(),
            ...overrides
        };
        vi.spyOn(useReportsHook, 'useReports').mockReturnValue(defaultValues as any);
        return defaultValues;
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('deve mostrar loading quando estiver carregando', () => {
        mockUseReports({ loading: true });
        render(<ReportsList />);
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('deve mostrar mensagem de lista vazia', () => {
        mockUseReports({ reports: [], loading: false });
        render(<ReportsList />);
        expect(screen.getByText('Nenhum relatório encontrado.')).toBeInTheDocument();
    });

    it('deve renderizar a lista de relatórios corretamente', () => {
        const mockReports = [
            {
                id: 1,
                title: 'Relatório Vendas Jan',
                category: 1,
                category_name: 'Vendas',
                reference_date: '2024-01-01',
                total_value: '1000.00',
                status: 'APPROVED',
                status_display: 'Aprovado'
            }
        ];
        mockUseReports({ reports: mockReports });

        render(<ReportsList />);

        expect(screen.getByText('Relatório Vendas Jan')).toBeInTheDocument();
        expect(screen.getByText('Vendas')).toBeInTheDocument();
        expect(screen.getByText('R$ 1.000,00')).toBeInTheDocument();
        // Verifica se o Chip de status está presente
        expect(screen.getByText('Aprovado')).toBeInTheDocument();
    });

    it('deve navegar para criar novo relatório ao clicar no botão', () => {
        mockUseReports();
        render(<ReportsList />);

        fireEvent.click(screen.getByText('Novo Relatório'));
        expect(mockNavigate).toHaveBeenCalledWith('/reports/new');
    });

    it('deve chamar fetchReports quando filtro mudar', () => {
        const { fetchReports } = mockUseReports();
        render(<ReportsList />);

        // Simula click no botao do mock do filtro
        fireEvent.click(screen.getByText('Aplicar Filtro'));

        expect(fetchReports).toHaveBeenCalledWith(expect.objectContaining({ status: 'APPROVED' }));
    });

    it('deve chamar removeReport ao clicar em excluir', async () => {
        const { removeReport } = mockUseReports({
            reports: [{ id: 1, title: 'R1', total_value: '10', status: 'PENDING' }]
        });

        render(<ReportsList />);

        const deleteButton = screen.getByLabelText('excluir');
        fireEvent.click(deleteButton);

        await waitFor(() => {
            expect(removeReport).toHaveBeenCalledWith(1);
        });
    });
});
