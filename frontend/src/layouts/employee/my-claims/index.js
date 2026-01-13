import { useEffect, useState } from "react";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

import { apiFetch } from "api";

export default function MyClaims() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    (async () => {
      const res = await apiFetch("/api/expenses/");
      const data = await res.json();
      setRows(Array.isArray(data) ? data : []);
    })();
  }, []);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <MDTypography variant="h4">My Claims</MDTypography>

        <MDBox mt={3}>
          {rows.length === 0 ? (
            <MDTypography variant="button">No claims yet.</MDTypography>
          ) : (
            rows.map((c) => (
              <MDBox
                key={c.id}
                p={2}
                mb={1.5}
                sx={{ border: "1px solid #eee", borderRadius: "12px" }}
              >
                <MDTypography variant="h6">{c.title}</MDTypography>
                <MDTypography variant="button">
                  Amount: {c.amount} | Status: {c.status}
                </MDTypography>
              </MDBox>
            ))
          )}
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}
