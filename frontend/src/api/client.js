const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function registerUser(payload) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function loginUser(payload) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchProfile(token) {
  return request("/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function fetchEvidencePackage(ticker, token) {
  return request(`/market/evidence/${ticker}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function runDebate(ticker, token) {
  return request(`/debate/${ticker}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function runVerdict(ticker, token) {
  return request(`/verdict/${ticker}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail ?? "Request failed");
  }
  return data;
}
