import React, { useState } from "react";
import WelcomeScreen from "./components/auth/WelcomeScreen.jsx";
import TraineeChoiceScreen from "./components/auth/TraineeChoiceScreen.jsx";
import TraineeLoginScreen from "./components/auth/TraineeLoginScreen.jsx";
import AdminLoginScreen from "./components/auth/AdminLoginScreen.jsx";
import RegisterScreen from "./components/auth/RegisterScreen.jsx";
import TraineeDashboard from "./components/trainee/TraineeDashboard.jsx";
import AdminDashboard from "./components/admin/AdminDashboard.jsx";

export default function App() {
  const [screen, setScreen] = useState("welcome");

  const goto = (next) => setScreen(next);

  return (
    <div className="sk-root">
      {screen === "welcome" && <WelcomeScreen goto={goto} />}
      {screen === "trainee-choice" && <TraineeChoiceScreen goto={goto} />}
      {screen === "trainee-login" && <TraineeLoginScreen goto={goto} />}
      {screen === "admin-login" && <AdminLoginScreen goto={goto} />}
      {screen === "register" && <RegisterScreen goto={goto} />}
      {screen === "trainee" && <TraineeDashboard />}
      {screen === "admin" && <AdminDashboard />}
    </div>
  );
}
