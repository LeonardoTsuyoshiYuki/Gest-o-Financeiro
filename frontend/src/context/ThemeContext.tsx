import React, { createContext, useContext, useState, useEffect } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme, Theme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';

type ThemeMode = 'light' | 'dark';

interface ThemeContextProps {
    mode: ThemeMode;
    toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextProps>({
    mode: 'light',
    toggleTheme: () => { },
});

export const useThemeMode = () => useContext(ThemeContext);

const getDesignTokens = (mode: ThemeMode) => ({
    palette: {
        mode,
        ...(mode === 'light'
            ? {
                // Premium Light
                primary: { main: '#2563EB' }, // Royal Blue
                secondary: { main: '#F59E0B' }, // Amber
                background: { default: '#F3F4F6', paper: '#FFFFFF' },
                text: { primary: '#111827', secondary: '#4B5563' }
            }
            : {
                // Premium Dark (Deep Navy)
                primary: { main: '#60A5FA' }, // Light Blue
                secondary: { main: '#FBBF24' }, // Light Amber
                background: { default: '#0B1120', paper: '#1F2937' },
                text: { primary: '#F9FAFB', secondary: '#9CA3AF' }
            }),
    },
    typography: {
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
        h4: { fontWeight: 700 },
        h6: { fontWeight: 600 },
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: { textTransform: 'none' as const },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: { borderRadius: 8 },
            },
        },
    },
});

export const CustomThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [mode, setMode] = useState<ThemeMode>(() => {
        const saved = localStorage.getItem('themeMode');
        return (saved as ThemeMode) || 'light';
    });

    useEffect(() => {
        localStorage.setItem('themeMode', mode);
    }, [mode]);

    const toggleTheme = () => {
        setMode((prev) => (prev === 'light' ? 'dark' : 'light'));
    };

    const theme = React.useMemo(() => createTheme(getDesignTokens(mode)), [mode]);

    return (
        <ThemeContext.Provider value={{ mode, toggleTheme }}>
            <MuiThemeProvider theme={theme}>
                <CssBaseline />
                {children}
            </MuiThemeProvider>
        </ThemeContext.Provider>
    );
};
