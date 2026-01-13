import { useState } from "react";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

import MDBox from "components/MDBox";
import MDButton from "components/MDButton";
import MDInput from "components/MDInput";
import MDTypography from "components/MDTypography";

import { apiFetch } from "api";

export default function SubmitClaim() {
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [receipt, setReceipt] = useState(null);
  const [msg, setMsg] = useState("");

  const onSubmit = async () => {
    setMsg("");
    const fd = new FormData();
    fd.append("title", title);
    fd.append("amount", amount);
    fd.append("category", "TRAVEL"); // you can change later to dropdown
    fd.append("description", description);
    if (receipt) fd.append("receipt", receipt);

    const res = await apiFetch("/api/expenses/", { method: "POST", body: fd });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      setMsg(err.detail || "Failed to submit claim");
      return;
    }

    setMsg("✅ Claim submitted!");
    setTitle("");
    setAmount("");
    setDescription("");
    setReceipt(null);
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <MDTypography variant="h4">Submit Claim</MDTypography>

        <MDBox mt={3} sx={{ maxWidth: 500 }} display="flex" flexDirection="column" gap={2}>
          <MDInput label="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <MDInput label="Amount" value={amount} onChange={(e) => setAmount(e.target.value)} />
          <MDInput
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={4}
          />

          <MDBox>
            <MDTypography variant="button" fontWeight="regular">
              Receipt (optional)
            </MDTypography>
            <input type="file" onChange={(e) => setReceipt(e.target.files?.[0] || null)} />
          </MDBox>

          <MDButton color="info" onClick={onSubmit}>
            Submit
          </MDButton>

          {msg && (
            <MDTypography variant="button" color="text">
              {msg}
            </MDTypography>
          )}
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}
