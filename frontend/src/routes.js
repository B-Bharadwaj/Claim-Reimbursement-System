import ProtectedRoute from "components/ProtectedRoute";

import EmployeeDashboard from "layouts/employee/dashboard";
import SubmitClaim from "layouts/employee/submit-claim";
import MyClaims from "layouts/employee/my-claims";

import ManagerReview from "layouts/manager/review-claims";
import FinancePayments from "layouts/finance/payments";
import SignIn from "layouts/authentication/sign-in";
// @mui icons
import Icon from "@mui/material/Icon";

// Layouts
import Dashboard from "layouts/dashboard";
import Expenses from "layouts/expenses";
const routes = [
  {
    type: "route",
    name: "Sign In",
    key: "sign-in",
    route: "/authentication/sign-in",
    component: <SignIn />,
  },
  {
    type: "collapse",
    name: "Dashboard",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: <Dashboard />,
  },
  {
    type: "collapse",
    name: "Expenses",
    key: "expenses",
    icon: <Icon fontSize="small">table_view</Icon>,
    route: "/expenses",
    component: <Expenses />,
  },
  {
    type: "route",
    name: "Employee Dashboard",
    key: "employee-dashboard",
    route: "/employee/dashboard",
    component: (
      <ProtectedRoute allowedRoles={["employee"]}>
        <EmployeeDashboard />
      </ProtectedRoute>
    ),
  },
  {
    type: "route",
    name: "Submit Claim",
    key: "submit-claim",
    route: "/employee/submit-claim",
    component: (
      <ProtectedRoute allowedRoles={["employee"]}>
        <SubmitClaim />
      </ProtectedRoute>
    ),
  },
  {
    type: "route",
    name: "My Claims",
    key: "my-claims",
    route: "/employee/my-claims",
    component: (
      <ProtectedRoute allowedRoles={["employee"]}>
        <MyClaims />
      </ProtectedRoute>
    ),
  },
  {
    type: "route",
    name: "Manager Review",
    key: "manager-review",
    route: "/manager/review",
    component: (
      <ProtectedRoute allowedRoles={["manager"]}>
        <ManagerReview />
      </ProtectedRoute>
    ),
  },
  {
    type: "route",
    name: "Finance Payments",
    key: "finance-payments",
    route: "/finance/payments",
    component: (
      <ProtectedRoute allowedRoles={["finance"]}>
        <FinancePayments />
      </ProtectedRoute>
    ),
  },
];

export default routes;
