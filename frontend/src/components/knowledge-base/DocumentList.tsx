"use client";

import { useEffect, useState } from "react";
import {
  FileText,
  FileSpreadsheet,
  File,
  Trash2,
  CheckCircle2,
  Clock,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { listDocuments, deleteDocument, processDocument } from "@/lib/api";
import type { Document } from "@/lib/types";

interface DocumentListProps {
  refreshKey?: number;
}

const fileIcons: Record<string, React.ElementType> = {
  pdf: FileText,
  docx: File,
  xlsx: FileSpreadsheet,
};

export default function DocumentList({ refreshKey }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = async () => {
    try {
      const data = await listDocuments("knowledge_base");
      setDocuments(data.documents);
    } catch (error) {
      console.error("Failed to fetch documents:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refreshKey]);

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this document? Its Q&A pairs will also be removed."))
      return;
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (error) {
      console.error("Failed to delete:", error);
    }
  };

  const handleReprocess = async (id: string) => {
    try {
      await processDocument(id);
      fetchDocuments();
    } catch (error) {
      console.error("Failed to reprocess:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8 text-gray-500">
        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
        Loading documents...
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-gray-500">
        No documents uploaded yet. Upload files above to build your knowledge
        base.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => {
        const Icon = fileIcons[doc.file_type] || File;
        return (
          <div
            key={doc.id}
            className="flex items-center justify-between rounded-lg border border-gray-200 px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <Icon className="h-5 w-5 text-gray-400" />
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {doc.filename}
                </p>
                <p className="text-xs text-gray-500">
                  Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {doc.processed ? (
                <Badge variant="success">
                  <CheckCircle2 className="mr-1 h-3 w-3" />
                  Processed
                </Badge>
              ) : (
                <Badge variant="warning">
                  <Clock className="mr-1 h-3 w-3" />
                  Pending
                </Badge>
              )}
              {!doc.processed && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleReprocess(doc.id)}
                  title="Process document"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              )}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDelete(doc.id)}
                className="text-gray-400 hover:text-red-500"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
