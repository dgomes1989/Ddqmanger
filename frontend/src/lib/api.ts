import axios from "axios";
import type {
  DocumentListResponse,
  FillRequest,
  FillRequestListResponse,
  KnowledgeBaseStats,
} from "./types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

// Documents
export async function uploadDocuments(
  files: File[],
  documentType: string = "knowledge_base"
) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const { data } = await api.post(
    `/api/documents/upload?document_type=${documentType}`,
    formData
  );
  return data;
}

export async function listDocuments(documentType?: string) {
  const params = documentType ? { document_type: documentType } : {};
  const { data } = await api.get<DocumentListResponse>("/api/documents", {
    params,
  });
  return data;
}

export async function deleteDocument(id: string) {
  await api.delete(`/api/documents/${id}`);
}

// Knowledge Base
export async function getKBStats() {
  const { data } = await api.get<KnowledgeBaseStats>(
    "/api/knowledge-base/stats"
  );
  return data;
}

export async function processDocument(documentId: string) {
  const { data } = await api.post(
    `/api/knowledge-base/process/${documentId}`
  );
  return data;
}

export async function processAllDocuments() {
  const { data } = await api.post("/api/knowledge-base/process-all");
  return data;
}

// Fill Requests
export async function createFillRequest(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<FillRequest>("/api/requests", formData);
  return data;
}

export async function listFillRequests() {
  const { data } = await api.get<FillRequestListResponse>("/api/requests");
  return data;
}

export async function getFillRequest(id: string) {
  const { data } = await api.get<FillRequest>(`/api/requests/${id}`);
  return data;
}

export async function updateFillRequestItem(
  requestId: string,
  itemId: string,
  update: { final_answer?: string; status?: string }
) {
  await api.patch(`/api/requests/${requestId}/items/${itemId}`, update);
}

export async function approveFillRequest(id: string) {
  await api.post(`/api/requests/${id}/approve`);
}

export async function exportFillRequest(id: string) {
  const response = await api.post(`/api/requests/${id}/export`, null, {
    responseType: "blob",
  });

  // Extract filename from Content-Disposition header
  const disposition = response.headers["content-disposition"];
  const filenameMatch = disposition?.match(/filename="?(.+)"?/);
  const filename = filenameMatch ? filenameMatch[1] : "ddq_filled.docx";

  // Trigger download
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
