export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

/** Richer error that preserves the API envelope fields callers need to branch on. */
export class ApiError extends Error {
  constructor(message, { status = 0, errorCode = null, data = null } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.errorCode = errorCode;
    this.data = data;
  }
}

async function parseResponse(response) {
  const body = await response.json().catch(() => ({}));
  if (response.status === 401) {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.dispatchEvent(new Event("skilloutcome:unauthorized"));
  }
  if (!response.ok) {
    const message = body.detail || body.message || "Something went wrong";
    throw new ApiError(message, {
      status: response.status,
      errorCode: body.error_code ?? null,
      data: body.data ?? null,
    });
  }
  return body;
}

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
  });
  return parseResponse(response);
}

export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
  return parseResponse(response);
}

export async function registerUser({ name, email, password, role }) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, email, password, role }) });
  return parseResponse(response);
}

export const getCurrentUser = () => apiRequest("/auth/me");
export const getMyTrainee = () => apiRequest("/trainees/me");
export const createTrainee = (payload) => apiRequest("/trainees", { method: "POST", body: JSON.stringify(payload) });
export const updateTrainee = (id, payload) => apiRequest(`/trainees/${id}`, { method: "PUT", body: JSON.stringify(payload) });
export const assignTraineeSkills = (id, skills) => apiRequest(`/trainees/${id}/skills`, { method: "POST", body: JSON.stringify({ skills }) });
export const getSkills = () => apiRequest("/skills");
export const getTrainingPrograms = () => apiRequest("/training");
export const enrollTrainee = (payload) => apiRequest("/training/enroll", { method: "POST", body: JSON.stringify(payload) });
export const getTrainingEnrollments = (id) => apiRequest(`/training/enrollments/${id}`);
export const getEmploymentHistory = (id) => apiRequest(`/employment/${id}`);
export const getFollowupHistory = (id) => apiRequest(`/followups/${id}`);
export const getDashboardAnalytics = () => apiRequest("/analytics/dashboard");
export const getProviderAnalytics = () => apiRequest("/analytics/providers");
export const getSkillGapAnalytics = () => apiRequest("/analytics/skill-gaps");
export const getDistrictAnalytics = () => apiRequest("/analytics/districts");
export const createFollowup = (payload) => apiRequest("/followups", { method: "POST", body: JSON.stringify(payload) });
export const createTrainingProgram = (payload) => apiRequest("/training", { method: "POST", body: JSON.stringify(payload) });
export const updateEnrollment = (id, payload) => apiRequest(`/training/enrollment/${id}`, { method: "PUT", body: JSON.stringify(payload) });
export const getAllTrainees = () => apiRequest("/trainees");
export const getTrainee = (id) => apiRequest(`/trainees/${id}`);
export const getEmployers = () => apiRequest("/employers");
export const getMyEmployer = () => apiRequest("/employers/me");
export const createEmployer = (payload) => apiRequest("/employers", { method: "POST", body: JSON.stringify(payload) });
export const updateEmployer = (id, payload) => apiRequest(`/employers/${id}`, { method: "PUT", body: JSON.stringify(payload) });
export const createEmploymentRecord = (payload) => apiRequest("/employment", { method: "POST", body: JSON.stringify(payload) });
export const getMyEmploymentRecords = () => apiRequest("/employment/mine");
export const updateEmploymentRecord = (id, payload) => apiRequest(`/employment/${id}`, { method: "PUT", body: JSON.stringify(payload) });
export const getMyTrainingPrograms = () => apiRequest("/training/mine");
export const getMyProviderEnrollments = () => apiRequest("/training/mine/enrollments");
export const updateEmployerVerification = (id, verification_status) => apiRequest(`/employers/${id}/verification`, { method: "PATCH", body: JSON.stringify({ verification_status }) });
export const getTraineeSkillGap = (traineeId, targetJobRole) =>
  apiRequest(`/trainees/${traineeId}/ml/skill-gap`, {
    method: "POST",
    body: JSON.stringify({ target_job_role: targetJobRole }),
  });
