export const API_BASE = "http://127.0.0.1:8000";

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("access");
  const headers = new Headers(options.headers || {});

  // If body is FormData, don't set content-type (browser will set boundary)
  const isFormData = options.body instanceof FormData;

  if (!isFormData && !headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  return res;
}
