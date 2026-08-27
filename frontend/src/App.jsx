import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import LoginScreen from "./components/auth/LoginScreen.jsx";
import RegisterScreen from "./components/auth/RegisterScreen.jsx";
import RoleScreen from "./components/auth/RoleScreen.jsx";
import TraineeDashboard from "./components/trainee/TraineeDashboard.jsx";
import AdminDashboard from "./components/admin/AdminDashboard.jsx";
import { I18nProvider } from "./i18n.jsx";

function EmployerDashboard(){
  return <div className="simple-page"><div className="sk-card simple-card"><h1 className="sk-display">Employer / Provider</h1><p>Provider workspace is ready for the next integration.</p></div></div>;
}

export default function App(){
  return <I18nProvider><Routes>
    <Route path="/" element={<Navigate to="/role" replace/>}/>
    <Route path="/role" element={<RoleScreen/>}/>
    <Route path="/login/:role" element={<LoginScreen/>}/>
    <Route path="/register/:role" element={<RegisterScreen/>}/>
    <Route path="/trainee/*" element={<TraineeDashboard/>}/>
    <Route path="/admin/*" element={<AdminDashboard/>}/>
    <Route path="/employer" element={<EmployerDashboard/>}/>
    <Route path="/login" element={<Navigate to="/role" replace/>}/>
    <Route path="/register" element={<Navigate to="/role" replace/>}/>
    <Route path="*" element={<Navigate to="/role" replace/>}/>
  </Routes></I18nProvider>;
}
