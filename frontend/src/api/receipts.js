import api from "./axios";

export async function uploadReceipt({ expenseId, file }) {
  const formData = new FormData();
  formData.append("expense", expenseId);
  formData.append("file", file);

  const res = await api.post("/api/receipts/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data; // contains ocr_status, ocr_result, etc.
}
