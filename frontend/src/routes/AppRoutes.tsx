import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '../features/dashboard/Dashboard';
import ReportsList from '../features/reports/ReportsList';

import ReportForm from '../features/reports/ReportForm';


import CategoriesList from '../features/categories/CategoriesList';
import CategoryForm from '../features/categories/CategoryForm';
import Login from '../features/auth/Login';
import InvoiceUpload from '../features/invoices/InvoiceUpload';
import InboxList from '../features/invoices/InboxList';
import UserList from '../features/users/UserList';
import PrivateRoute from './PrivateRoute';
import MainLayout from '../layout/MainLayout';

// const Dashboard = () => <h1>Dashboard (Em construção)</h1>;
// const CategoriesList = () => <h1>Categorias (Em c*onstrução)</h1>;

const AppRoutes: React.FC = () => {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />

            <Route element={<PrivateRoute />}>
                <Route element={<MainLayout />}>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/reports" element={<ReportsList />} />
                    <Route path="/reports/new" element={<ReportForm />} />
                    <Route path="/reports/:id" element={<ReportForm />} />
                    <Route path="/categories" element={<CategoriesList />} />
                    <Route path="/categories/new" element={<CategoryForm />} />
                    <Route path="/categories/:id" element={<CategoryForm />} />
                    <Route path="/invoices/upload" element={<InvoiceUpload />} />
                    <Route path="/invoices/inbox" element={<InboxList />} />
                    <Route path="/users" element={<UserList />} />
                </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
};

export default AppRoutes;
