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

export default function Payments() {
  const [claims, setClaims] = useState([]);
  const [paymentRefById, setPaymentRefById] = useState({});
  const [commentById, setCommentById] = useState({});

  const load = async () => {
    const res = await apiFetch("/api/expenses/");
    const data = await res.json();
    setClaims(Array.isArray(data) ? data : []);
  };

  useEffect(() => {
    load();
  }, []);

  const financeApprove = async (id) => {
    const body = { finance_comment: commentById[id] || "" };

    const res = await apiFetch(`/api/expenses/${id}/finance_approve/`, {
      method: "POST",
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || "Finance approve failed");
      return;
    }
    await load();
  };

  const markPaid = async (id) => {
    const body = { payment_reference: paymentRefById[id] || "" };

    const res = await apiFetch(`/api/expenses/${id}/mark_paid/`, {
      method: "POST",
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || "Mark paid failed");
      return;
    }
    await load();
  };

  const financeQueue = claims.filter(
    (c) => c.status === "MANAGER_APPROVED" || c.status === "FINANCE_APPROVED"
  );

  const columns = [
    { Header: "Title", accessor: "title" },
    { Header: "Amount", accessor: "amount" },
    { Header: "Status", accessor: "status" },
    { Header: "Receipt", accessor: "receipt" },
    { Header: "Finance comment", accessor: "comment" },
    { Header: "Payment ref", accessor: "ref" },
    { Header: "Actions", accessor: "actions" },
  ];

  const rows = financeQueue.map((c) => ({
    title: c.title,
    amount: c.amount,
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
        placeholder="Finance comment..."
        value={commentById[c.id] || ""}
        onChange={(e) => setCommentById((p) => ({ ...p, [c.id]: e.target.value }))}
      />
    ),
    ref: (
      <MDInput
        size="small"
        placeholder="Payment reference..."
        value={paymentRefById[c.id] || ""}
        onChange={(e) => setPaymentRefById((p) => ({ ...p, [c.id]: e.target.value }))}
      />
    ),
    actions: (
      <MDBox display="flex" gap={1}>
        {c.status === "MANAGER_APPROVED" && (
          <MDButton color="info" size="small" onClick={() => financeApprove(c.id)}>
            Finance Approve
          </MDButton>
        )}
        {c.status === "FINANCE_APPROVED" && (
          <MDButton color="success" size="small" onClick={() => markPaid(c.id)}>
            Mark Paid
          </MDButton>
        )}
      </MDBox>
    ),
  }));

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <MDTypography variant="h4">Payments</MDTypography>
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
              No claims in finance queue.
            </MDTypography>
          )}
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}
