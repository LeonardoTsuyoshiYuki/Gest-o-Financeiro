import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ExecutiveKPIs from '../components/ExecutiveKPIs';

describe('ExecutiveKPIs', () => {
    const mockData = {
        current_month_total: 1500.0,
        last_month_total: 1200.0,
        variation_percent: 25.0,
        import_errors_count: 2,
        skipped_count: 1,
        report_count: 5,
        insights_list: ["Insight 1", "Insight 2"]
    };

    it('displays loading state', () => {
        render(<ExecutiveKPIs data={null} loading={true} />);
        expect(screen.getByText('Carregando painel executivo...')).toBeInTheDocument();
    });

    it('renders KPI values correctly', () => {
        render(<ExecutiveKPIs data={mockData} loading={false} />);

        // Verifica titulos dos cards
        expect(screen.getByText('DESPESAS (MÊS ATUAL)')).toBeInTheDocument();
        expect(screen.getByText('VOLUME DE FATURAS')).toBeInTheDocument();
        expect(screen.getByText('ATENÇÃO NECESSÁRIA')).toBeInTheDocument();

        // Verifica valores formatados em BRL (aproximado)
        // O teste de locale pode variar dependendo do ambiente, mas BRL geralmente tem R$ ou ,00
        const totalElement = screen.getByText((content) => content.includes('1.500,00') || content.includes('1500'));
        expect(totalElement).toBeInTheDocument();

        // Verifica contagens
        expect(screen.getByText('5')).toBeInTheDocument(); // Reports
        expect(screen.getByText('3')).toBeInTheDocument(); // 2 errors + 1 skipped
    });

    it('renders insights alerts', () => {
        render(<ExecutiveKPIs data={mockData} loading={false} />);
        expect(screen.getByText('Insight 1')).toBeInTheDocument();
        expect(screen.getByText('Insight 2')).toBeInTheDocument();
    });

    it('navigates error visuals correctly', () => {
        render(<ExecutiveKPIs data={mockData} loading={false} />);
        expect(screen.getByText('2 Erros')).toBeInTheDocument();
        expect(screen.getByText('1 Duplicadas')).toBeInTheDocument();
    });
});
