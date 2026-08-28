import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import LoginScreen from "./components/auth/LoginScreen.jsx";
import RegisterScreen from "./components/auth/RegisterScreen.jsx";
import RoleScreen from "./components/auth/RoleScreen.jsx";
import TraineeDashboard from "./components/trainee/TraineeDashboard.jsx";
import AdminDashboard from "./components/admin/AdminDashboard.jsx";
import EmployerDashboard from "./components/employer/EmployerDashboard.jsx";
import ProviderDashboard from "./components/provider/ProviderDashboard.jsx";
import { AuthProvider } from "./auth/AuthContext.jsx";
import ProtectedRoute from "./auth/ProtectedRoute.jsx";
import { I18nProvider } from "./i18n.jsx";

export default function App(){
  return <I18nProvider><AuthProvider><Routes>
    <Route path="/" element={<Navigate to="/role" replace/>}/>
    <Route path="/role" element={<RoleScreen/>}/>
    <Route path="/login/:role" element={<LoginScreen/>}/>
    <Route path="/register/:role" element={<RegisterScreen/>}/>
    <Route element={<ProtectedRoute allowedRoles={["TRAINEE"]}/>}><Route path="/trainee/*" element={<TraineeDashboard/>}/></Route>
    <Route element={<ProtectedRoute allowedRoles={["ADMIN"]}/>}><Route path="/admin/*" element={<AdminDashboard/>}/></Route>
    <Route element={<ProtectedRoute allowedRoles={["EMPLOYER"]}/>}><Route path="/employer" element={<EmployerDashboard/>}/></Route>
    <Route element={<ProtectedRoute allowedRoles={["PROVIDER"]}/>}><Route path="/provider/*" element={<ProviderDashboard/>}/></Route>
    <Route path="/login" element={<Navigate to="/role" replace/>}/>
    <Route path="/register" element={<Navigate to="/role" replace/>}/>
    <Route path="*" element={<Navigate to="/role" replace/>}/>
  </Routes></AuthProvider></I18nProvider>;
}
