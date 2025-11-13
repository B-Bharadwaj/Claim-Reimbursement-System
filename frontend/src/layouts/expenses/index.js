// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";

// React hooks
import { useEffect, useState } from "react";

// API base URL
import { API_BASE } from "api";

function Expenses() {
  const [rows, setRows] = useState([]);
  const columns = [
    { Header: "Title", accessor: "title", width: "30%" },
    { Header: "Amount", accessor: "amount", width: "20%" },
    { Header: "Status", accessor: "status", width: "20%" },
  ];

  useEffect(() => {
    const fetchExpenses = async () => {
      try {
        const res = await fetch(`${API_BASE}expenses/`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access")}`,
          },
        });
        const data = await res.json();
        // Transform API data to DataTable rows
        const formatted = data.map((exp) => ({
          title: exp.title,
          amount: exp.amount,
          status: exp.status,
        }));
        setRows(formatted);
      } catch (err) {
        console.error("Failed to load expenses:", err);
      }
    };

    fetchExpenses();
  }, []);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <MDTypography variant="h6" color="white">
                  Expenses
                </MDTypography>
              </MDBox>
              <MDBox pt={3}>
                <DataTable
                  table={{ columns, rows }}
                  isSorted={false}
                  entriesPerPage={false}
                  showTotalEntries={false}
                  noEndBorder
                />
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Expenses;
