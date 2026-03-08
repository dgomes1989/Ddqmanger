"use client";

import { useEffect, useState } from "react";
import { BookOpen, Database, HelpCircle, MessageSquare } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import FileUploader from "@/components/knowledge-base/FileUploader";
import DocumentList from "@/components/knowledge-base/DocumentList";
import { getKBStats } from "@/lib/api";
import type { KnowledgeBaseStats } from "@/lib/types";

export default function KnowledgeBasePage() {
  const [stats, setStats] = useState<KnowledgeBaseStats | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchStats = () => {
    getKBStats()
      .then(setStats)
      .catch(() => setStats(null));
  };

  useEffect(() => {
    fetchStats();
  }, [refreshKey]);

  const handleUploadComplete = () => {
    setRefreshKey((k) => k + 1);
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Knowledge Base</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload filled DDQs and materials to build your knowledge base. The AI
          will extract question-answer pairs for auto-populating future requests.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-lg bg-blue-100 p-3">
              <Database className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Documents</p>
              <p className="text-xl font-bold">
                {stats
                  ? `${stats.processed_documents}/${stats.total_documents}`
                  : "—"}
              </p>
              <p className="text-xs text-gray-400">processed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-lg bg-green-100 p-3">
              <HelpCircle className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Questions</p>
              <p className="text-xl font-bold">
                {stats?.total_questions ?? "—"}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-lg bg-purple-100 p-3">
              <MessageSquare className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Answers</p>
              <p className="text-xl font-bold">
                {stats?.total_answers ?? "—"}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upload section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Upload Materials
          </CardTitle>
          <CardDescription>
            Upload previously filled DDQs, investor presentations, pitch decks,
            and other materials. We support PDF, Word (.docx), and Excel (.xlsx)
            files.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FileUploader onUploadComplete={handleUploadComplete} />
        </CardContent>
      </Card>

      {/* Document list */}
      <Card>
        <CardHeader>
          <CardTitle>Uploaded Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <DocumentList refreshKey={refreshKey} />
        </CardContent>
      </Card>
    </div>
  );
}
