"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  FileText,
  Clock,
  CheckCircle2,
  Download,
  Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { createFillRequest, listFillRequests } from "@/lib/api";
import type { FillRequest } from "@/lib/types";

export default function FillRequestPage() {
  const router = useRouter();
  const [requests, setRequests] = useState<FillRequest[]>([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    listFillRequests()
      .then((data) => setRequests(data.requests))
      .catch(() => setRequests([]));
  }, []);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;
      setUploading(true);
      try {
        const result = await createFillRequest(acceptedFiles[0]);
        router.push(`/fill-request/${result.id}`);
      } catch (error) {
        console.error("Failed to create fill request:", error);
        setUploading(false);
      }
    },
    [router]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ],
    },
    maxFiles: 1,
  });

  const statusConfig: Record<
    string,
    { label: string; variant: "default" | "warning" | "success" | "secondary" | "destructive"; icon: React.ElementType }
  > = {
    processing: { label: "Processing", variant: "warning", icon: Clock },
    draft: { label: "Draft", variant: "default", icon: FileText },
    approved: { label: "Approved", variant: "success", icon: CheckCircle2 },
    exported: { label: "Exported", variant: "secondary", icon: Download },
    error: { label: "Error", variant: "destructive", icon: Clock },
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Fill Request</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload an unfilled DDQ or investor request. The AI will populate
          answers from your knowledge base.
        </p>
      </div>

      {/* Upload new DDQ */}
      <Card>
        <CardHeader>
          <CardTitle>New Request</CardTitle>
          <CardDescription>
            Upload an unfilled DDQ document. We&apos;ll extract the questions and
            auto-populate answers from your knowledge base.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {uploading ? (
            <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-blue-300 bg-blue-50 p-8">
              <Loader2 className="mb-3 h-10 w-10 animate-spin text-blue-500" />
              <p className="text-sm font-medium text-blue-700">
                Uploading and processing your DDQ...
              </p>
              <p className="mt-1 text-xs text-blue-500">
                This may take a minute while the AI extracts questions and finds
                answers.
              </p>
            </div>
          ) : (
            <div
              {...getRootProps()}
              className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors ${
                isDragActive
                  ? "border-blue-400 bg-blue-50"
                  : "border-gray-300 hover:border-gray-400"
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="mb-3 h-10 w-10 text-gray-400" />
              <p className="text-sm font-medium text-gray-700">
                {isDragActive
                  ? "Drop your DDQ here..."
                  : "Drop an unfilled DDQ here, or click to browse"}
              </p>
              <p className="mt-1 text-xs text-gray-500">
                Supports PDF, Word (.docx), and Excel (.xlsx)
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Previous requests */}
      {requests.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Previous Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {requests.map((req) => {
                const config = statusConfig[req.status] || statusConfig.processing;
                const StatusIcon = config.icon;
                return (
                  <Link
                    key={req.id}
                    href={`/fill-request/${req.id}`}
                    className="flex items-center justify-between rounded-lg border border-gray-200 px-4 py-3 transition-colors hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {req.document_filename || "Untitled"}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(req.created_at).toLocaleDateString()}{" "}
                          &middot; {req.items.length} questions
                        </p>
                      </div>
                    </div>
                    <Badge variant={config.variant}>
                      <StatusIcon className="mr-1 h-3 w-3" />
                      {config.label}
                    </Badge>
                  </Link>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
