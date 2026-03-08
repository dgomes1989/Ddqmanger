"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  BookOpen,
  FileText,
  Database,
  HelpCircle,
  MessageSquare,
  ArrowRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getKBStats, listFillRequests } from "@/lib/api";
import type { KnowledgeBaseStats, FillRequest } from "@/lib/types";

export default function Dashboard() {
  const [stats, setStats] = useState<KnowledgeBaseStats | null>(null);
  const [recentRequests, setRecentRequests] = useState<FillRequest[]>([]);

  useEffect(() => {
    getKBStats()
      .then(setStats)
      .catch(() => setStats(null));
    listFillRequests()
      .then((data) => setRecentRequests(data.requests.slice(0, 5)))
      .catch(() => setRecentRequests([]));
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your knowledge base and fill DDQ requests with AI assistance.
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-lg bg-blue-100 p-3">
              <Database className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Documents</p>
              <p className="text-2xl font-bold">
                {stats?.total_documents ?? "—"}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-lg bg-green-100 p-3">
              <HelpCircle className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Questions</p>
              <p className="text-2xl font-bold">
                {stats?.total_questions ?? "—"}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-lg bg-purple-100 p-3">
              <MessageSquare className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Answers</p>
              <p className="text-2xl font-bold">
                {stats?.total_answers ?? "—"}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-lg bg-amber-100 p-3">
              <FileText className="h-6 w-6 text-amber-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Requests</p>
              <p className="text-2xl font-bold">{recentRequests.length}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-blue-600" />
              Knowledge Base
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">
              Upload previously filled DDQs, investor presentations, and other
              materials to build your knowledge base. The AI will extract
              question-answer pairs for future use.
            </p>
            <Link href="/knowledge-base">
              <Button>
                Manage Knowledge Base
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              Fill New Request
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">
              Upload an unfilled DDQ or investor request. The AI will populate
              answers from your knowledge base, flag conflicts, and let you
              review before exporting.
            </p>
            <Link href="/fill-request">
              <Button>
                Start New Request
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recent requests */}
      {recentRequests.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {recentRequests.map((req) => (
                <Link
                  key={req.id}
                  href={`/fill-request/${req.id}`}
                  className="flex items-center justify-between rounded-lg border border-gray-200 px-4 py-3 hover:bg-gray-50"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {req.document_filename || "Untitled"}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(req.created_at).toLocaleDateString()} &middot;{" "}
                      {req.items.length} questions
                    </p>
                  </div>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium ${
                      req.status === "draft"
                        ? "bg-blue-100 text-blue-700"
                        : req.status === "approved"
                        ? "bg-green-100 text-green-700"
                        : req.status === "exported"
                        ? "bg-gray-100 text-gray-700"
                        : "bg-amber-100 text-amber-700"
                    }`}
                  >
                    {req.status}
                  </span>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
