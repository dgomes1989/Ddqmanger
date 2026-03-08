"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  Download,
  Loader2,
  AlertTriangle,
  FileText,
} from "lucide-react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import QuestionRow from "@/components/fill-request/QuestionRow";
import {
  getFillRequest,
  approveFillRequest,
  exportFillRequest,
} from "@/lib/api";
import type { FillRequest } from "@/lib/types";

export default function FillRequestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [request, setRequest] = useState<FillRequest | null>(null);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState(false);
  const [exporting, setExporting] = useState(false);

  const fetchRequest = async () => {
    try {
      const data = await getFillRequest(id);
      setRequest(data);
    } catch (error) {
      console.error("Failed to fetch request:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequest();
    // Poll while processing
    const interval = setInterval(async () => {
      try {
        const data = await getFillRequest(id);
        setRequest(data);
        if (data.status !== "processing") {
          clearInterval(interval);
        }
      } catch {
        clearInterval(interval);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [id]);

  const handleApprove = async () => {
    setApproving(true);
    try {
      await approveFillRequest(id);
      await fetchRequest();
    } catch (error) {
      console.error("Failed to approve:", error);
    } finally {
      setApproving(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      await exportFillRequest(id);
      await fetchRequest();
    } catch (error) {
      console.error("Failed to export:", error);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  if (!request) {
    return (
      <div className="py-20 text-center">
        <p className="text-gray-500">Request not found.</p>
        <Link href="/fill-request" className="mt-2 text-blue-600 hover:underline">
          Back to requests
        </Link>
      </div>
    );
  }

  const conflictCount = request.items.filter((i) => i.has_conflict).length;
  const answeredCount = request.items.filter(
    (i) => i.suggested_answer || i.final_answer
  ).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link
            href="/fill-request"
            className="mb-2 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to requests
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">
            {request.document_filename || "Untitled DDQ"}
          </h1>
          <div className="mt-2 flex items-center gap-3">
            <Badge
              variant={
                request.status === "draft"
                  ? "default"
                  : request.status === "approved"
                  ? "success"
                  : request.status === "exported"
                  ? "secondary"
                  : "warning"
              }
            >
              {request.status}
            </Badge>
            <span className="text-sm text-gray-500">
              {request.items.length} questions &middot; {answeredCount} answered
            </span>
            {conflictCount > 0 && (
              <Badge variant="warning">
                <AlertTriangle className="mr-1 h-3 w-3" />
                {conflictCount} conflict(s)
              </Badge>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          {request.status === "draft" && (
            <Button onClick={handleApprove} disabled={approving}>
              {approving ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle2 className="h-4 w-4" />
              )}
              Approve Draft
            </Button>
          )}
          {(request.status === "approved" || request.status === "draft") && (
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={exporting}
            >
              {exporting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              Export
            </Button>
          )}
        </div>
      </div>

      {/* Processing state */}
      {request.status === "processing" && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Loader2 className="mb-4 h-10 w-10 animate-spin text-blue-500" />
            <h3 className="text-lg font-medium text-gray-900">
              Processing your DDQ...
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              The AI is extracting questions and finding answers from your
              knowledge base. This page will update automatically.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Questions list */}
      {request.items.length > 0 && (
        <div className="space-y-3">
          {request.items.map((item) => (
            <QuestionRow
              key={item.id}
              requestId={request.id}
              item={item}
              onUpdate={fetchRequest}
            />
          ))}
        </div>
      )}

      {/* Empty state for non-processing */}
      {request.items.length === 0 && request.status !== "processing" && (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="mx-auto h-10 w-10 text-gray-300" />
            <p className="mt-4 text-sm text-gray-500">
              No questions were extracted from this document.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
