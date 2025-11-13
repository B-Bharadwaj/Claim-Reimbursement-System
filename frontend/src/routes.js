// @mui icons
import Icon from "@mui/material/Icon";

// Layouts
import Dashboard from "layouts/dashboard";
import Expenses from "layouts/expenses";

const routes = [
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
];

export default routes;
