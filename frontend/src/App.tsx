import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { CustomThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import AppRoutes from './routes/AppRoutes';
import { SnackbarProvider } from 'notistack';

const App: React.FC = () => {
    return (
        <CustomThemeProvider>
            <SnackbarProvider maxSnack={3}>
                <BrowserRouter>
                    <AuthProvider>
                        <AppRoutes />
                    </AuthProvider>
                </BrowserRouter>
            </SnackbarProvider>
        </CustomThemeProvider>
    );
};

export default App;
