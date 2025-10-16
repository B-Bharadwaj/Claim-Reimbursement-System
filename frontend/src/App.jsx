import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import EmployeeSubmit from "./pages/EmployeeSubmit";
import MyExpenses from "./pages/MyExpenses";
import ManagerApprovals from "./pages/ManagerApprovals";
import FinancePayments from "./pages/FinancePayments";

export default function App() {
  return (
    <Router>
      <Navbar />
      <div className="p-6">
        <Routes>
          <Route path="/" element={<EmployeeSubmit />} />
          <Route path="/my-expenses" element={<MyExpenses />} />
          <Route path="/manager" element={<ManagerApprovals />} />
          <Route path="/finance" element={<FinancePayments />} />
        </Routes>
      </div>
    </Router>
  );
}
