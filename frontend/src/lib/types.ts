export interface Document {
  id: string;
  filename: string;
  file_type: string;
  document_type: string;
  uploaded_at: string;
  processed: boolean;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface KnowledgeBaseStats {
  total_documents: number;
  processed_documents: number;
  total_questions: number;
  total_answers: number;
}

export interface FillRequestItem {
  id: string;
  question_text: string;
  question_index: number;
  suggested_answer: string | null;
  final_answer: string | null;
  has_conflict: boolean;
  conflicting_answers: Array<{ text: string; source: string }> | null;
  status: string;
}

export interface FillRequest {
  id: string;
  document_id: string;
  document_filename: string | null;
  status: string;
  items: FillRequestItem[];
  created_at: string;
  updated_at: string;
}

export interface FillRequestListResponse {
  requests: FillRequest[];
  total: number;
}
