export const API_BASE = "http://127.0.0.1:8000";

let isRefreshing = false;
let refreshPromise = null;

async function refreshAccessToken() {
  const refresh = localStorage.getItem("refresh");
  if (!refresh) return false;

  // IMPORTANT: adjust endpoint if your backend uses a different refresh URL
  const res = await fetch(`${API_BASE}/api/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!res.ok) return false;

  const data = await res.json().catch(() => null);
  if (!data?.access) return false;

  localStorage.setItem("access", data.access);
  return true;
}

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("access");
  const headers = new Headers(options.headers || {});

  const isFormData = options.body instanceof FormData;
  if (!isFormData && !headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) headers.set("Authorization", `Bearer ${token}`);

  let res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // If token expired, backend usually returns 401.
  // Some setups return 400 with token_not_valid; we'll handle both.
  if (res.status === 401 || res.status === 400) {
    // Try to detect token_not_valid message (optional)
    const cloned = res.clone();
    const errData = await cloned.json().catch(() => null);
    const tokenExpired =
      errData?.code === "token_not_valid" ||
      errData?.messages?.some((m) => m.message?.toLowerCase()?.includes("expired"));

    if (tokenExpired) {
      if (!isRefreshing) {
        isRefreshing = true;
        refreshPromise = refreshAccessToken().finally(() => {
          isRefreshing = false;
        });
      }

      const ok = await refreshPromise;
      if (!ok) {
        // Refresh failed -> force logout
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("role");
        return res; // caller will show error; or you can redirect here
      }

      // Retry original request with new access token
      const newToken = localStorage.getItem("access");
      const retryHeaders = new Headers(options.headers || {});
      if (!isFormData && !retryHeaders.has("Content-Type") && options.body) {
        retryHeaders.set("Content-Type", "application/json");
      }
      if (newToken) retryHeaders.set("Authorization", `Bearer ${newToken}`);

      res = await fetch(`${API_BASE}${path}`, { ...options, headers: retryHeaders });
    }
  }

  return res;
}

export async function apiJson(path, options = {}) {
  const res = await apiFetch(path, options);
  const data = await res.json().catch(() => null);
  return { res, data };
}

export async function uploadReceipt(expenseId, file) {
  const fd = new FormData();
  fd.append("expense", String(expenseId));
  fd.append("file", file);

  const { res, data } = await apiJson("/api/receipts/", { method: "POST", body: fd });
  if (!res.ok) {
    const message = data?.detail || data?.error || "Receipt upload/OCR failed";
    throw new Error(message);
  }
  return data; // includes ocr_status + ocr_result
}
export async function fetchReceiptBlob(expenseId, download = false) {
  const res = await apiFetch(`/api/expenses/${expenseId}/receipt/?download=${download ? 1 : 0}`, {
    method: "GET",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch receipt");
  }

  return await res.blob();
}
