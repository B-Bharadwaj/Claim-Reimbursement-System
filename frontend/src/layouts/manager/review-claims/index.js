/* eslint-disable prettier/prettier */
import { useEffect, useState } from "react";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import MDInput from "components/MDInput";

import DataTable from "examples/Tables/DataTable";
import { apiFetch, fetchReceiptBlob } from "api";

const viewReceipt = async (expenseId) => {
  const blob = await fetchReceiptBlob(expenseId, false);
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank", "noopener,noreferrer");
};

const downloadReceipt = async (expenseId) => {
  const blob = await fetchReceiptBlob(expenseId, true);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `receipt_${expenseId}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
};

export default function ReviewClaims() {
  const [claims, setClaims] = useState([]);
  const [commentById, setCommentById] = useState({});

  const load = async () => {
    const res = await apiFetch("/api/expenses/");
    const data = await res.json();
    setClaims(Array.isArray(data) ? data : []);
  };

  useEffect(() => {
    load();
  }, []);

  const act = async (id, action) => {
    const body = { manager_comment: commentById[id] || "" };

    const res = await apiFetch(`/api/expenses/${id}/${action}/`, {
      method: "POST",
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || "Action failed");
      return;
    }
    await load();
  };

  // Only show SUBMITTED in UI (backend already filters, this is extra safe)
  const submitted = claims.filter((c) => c.status === "SUBMITTED");

  const columns = [
    { Header: "Title", accessor: "title" },
    { Header: "Amount", accessor: "amount" },
    { Header: "Category", accessor: "category" },
    { Header: "Status", accessor: "status" },
    { Header: "Receipt", accessor: "receipt" },
    { Header: "Comment", accessor: "comment" },
    { Header: "Actions", accessor: "actions" },
  ];

  const rows = submitted.map((c) => ({
    title: c.title,
    amount: c.amount,
    category: c.category,
    status: c.status,
    receipt: c.has_receipt ? (
      <MDBox display="flex" gap={1}>
        <MDButton color="info" size="small" variant="outlined" onClick={() => viewReceipt(c.id)}>
          View
        </MDButton>
        <MDButton color="dark" size="small" variant="outlined" onClick={() => downloadReceipt(c.id)}>
          Download
        </MDButton>
      </MDBox>
    ) : (
      <MDTypography variant="button" color="text">
        —
      </MDTypography>
    ),
    comment: (
      <MDInput
        size="small"
        placeholder="Manager comment..."
        value={commentById[c.id] || ""}
        onChange={(e) => setCommentById((p) => ({ ...p, [c.id]: e.target.value }))}
      />
    ),
    actions: (
      <MDBox display="flex" gap={1}>
        <MDButton color="success" size="small" onClick={() => act(c.id, "manager_approve")}>
          Approve
        </MDButton>
        <MDButton color="error" size="small" onClick={() => act(c.id, "manager_reject")}>
          Reject
        </MDButton>
      </MDBox>
    ),
  }));

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <MDTypography variant="h4">Review Claims</MDTypography>
        <MDBox mt={3}>
          <DataTable
            table={{ columns, rows }}
            isSorted={false}
            entriesPerPage={false}
            showTotalEntries={false}
            noEndBorder
          />
          {rows.length === 0 && (
            <MDTypography variant="button" mt={2}>
              No submitted claims to review.
            </MDTypography>
          )}
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}
