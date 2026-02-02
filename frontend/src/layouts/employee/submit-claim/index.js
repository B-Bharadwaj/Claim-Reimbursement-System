/* eslint-disable prettier/prettier */
import { useState } from "react";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";


import MDBox from "components/MDBox";
import MDButton from "components/MDButton";
import MDInput from "components/MDInput";
import MDTypography from "components/MDTypography";

import { apiJson, uploadReceipt } from "api";

export default function SubmitClaim() {
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [receipt, setReceipt] = useState(null);
  const [msg, setMsg] = useState("");
  const [ocrInfo, setOcrInfo] = useState(null); // {status, confidence, error}
  const [draftExpenseId, setDraftExpenseId] = useState(null);

  const createDraftExpense = async () => {
    const fd = new FormData();

    // Ensure backend validations always pass
    fd.append("title", title && title.trim() ? title.trim() : "Receipt Draft");
    fd.append("amount", amount && amount.trim() ? amount.trim() : "1");
    fd.append("category", "TRAVEL");
    fd.append("description", description || "");

    const { res, data } = await apiJson("/api/expenses/", { method: "POST", body: fd });

    if (!res.ok) {
      console.error("Draft create error:", data);
      const message =
        data?.detail ||
        data?.title?.[0] ||
        data?.amount?.[0] ||
        data?.category?.[0] ||
        "Failed to create draft expense";
      throw new Error(message);
    }

    setDraftExpenseId(data.id);
    return data.id;
  };


  const onAutofillFromReceipt = async () => {
  if (!receipt) {
    setMsg("Please choose a receipt file first.");
    return;
  }

  setMsg("");
  setOcrInfo(null);

  try {
    // 1) Create draft expense to get an ID (required by /api/receipts/)
    const expenseId = draftExpenseId || (await createDraftExpense());

    // 2) Upload receipt -> OCR
    const data = await uploadReceipt(expenseId, receipt);

    setOcrInfo({
      status: data.ocr_status,
      confidence: data.ocr_confidence,
      error: data.ocr_error,
    });

    if (data.ocr_status === "SUCCESS" && data.ocr_result) {
      if (data.ocr_result.vendor) setTitle(data.ocr_result.vendor);
      if (data.ocr_result.total_amount != null) setAmount(String(data.ocr_result.total_amount));

      // Optional: store receipt date into description (since your Expense model doesn't have date)
      if (data.ocr_result.date) {
        const tag = `Receipt Date: ${data.ocr_result.date}`;
        setDescription((prev) => (prev ? `${prev}\n${tag}` : tag));
      }

      setMsg("✅ Autofill completed. Please review and submit.");
    } else {
      setMsg("OCR failed. Please fill details manually and submit.");
    }
  } catch (e) {
    setOcrInfo({ status: "FAILED", confidence: null, error: e.message });
    setMsg(e.message);
  }
};


  const onSubmit = async () => {
    setMsg("");

    try {
      // Ensure we have a draft expense to submit
      const expenseId = draftExpenseId || (await createDraftExpense());

      // Update the draft with final user-edited values
      const fd = new FormData();
      fd.append("title", title);
      fd.append("amount", amount);
      fd.append("category", "TRAVEL");
      fd.append("description", description);

      const { res, data } = await apiJson(`/api/expenses/${expenseId}/`, { method: "PATCH", body: fd });

      if (!res.ok) {
        const message = data?.detail || "Failed to submit claim";
        setMsg(message);
        return;
      }

      setMsg("Claim submitted!");
      setTitle("");
      setAmount("");
      setDescription("");
      setReceipt(null);
      setDraftExpenseId(null);
      setOcrInfo(null);
    } catch (e) {
      setMsg(e.message || "Failed to submit claim");
    }
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
            <input
              type="file"
              accept="image/*,application/pdf"
              onChange={(e) => setReceipt(e.target.files?.[0] || null)}
            />

            <MDBox mt={1} display="flex" gap={1}>
              <MDButton color="info" variant="outlined" onClick={onAutofillFromReceipt} disabled={!receipt}>
                Autofill from Receipt
              </MDButton>
            </MDBox>

            {ocrInfo && (
              <MDBox mt={1}>
                <MDTypography variant="button">OCR: {ocrInfo.status}</MDTypography>
                {ocrInfo.confidence != null && (
                  <MDTypography variant="button">
                    Confidence: {(ocrInfo.confidence * 100).toFixed(0)}%
                  </MDTypography>
                )}
                {ocrInfo.error && (
                  <MDTypography variant="button" color="error">
                    OCR Error: {ocrInfo.error}
                  </MDTypography>
                )}
              </MDBox>
            )}
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
    </DashboardLayout>
  );
}
