"use client";

import { useState } from "react";
import { AlertTriangle, Check, Edit3, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { FillRequestItem } from "@/lib/types";
import { updateFillRequestItem } from "@/lib/api";

interface QuestionRowProps {
  requestId: string;
  item: FillRequestItem;
  onUpdate?: () => void;
}

export default function QuestionRow({ requestId, item, onUpdate }: QuestionRowProps) {
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(
    item.final_answer || item.suggested_answer || ""
  );
  const [showConflicts, setShowConflicts] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateFillRequestItem(requestId, item.id, {
        final_answer: editValue,
        status: "edited",
      });
      setEditing(false);
      onUpdate?.();
    } catch (error) {
      console.error("Failed to save:", error);
    } finally {
      setSaving(false);
    }
  };

  const handleAccept = async () => {
    try {
      await updateFillRequestItem(requestId, item.id, {
        final_answer: item.suggested_answer ?? undefined,
        status: "accepted",
      });
      onUpdate?.();
    } catch (error) {
      console.error("Failed to accept:", error);
    }
  };

  const selectConflictingAnswer = (text: string) => {
    setEditValue(text);
    setEditing(true);
    setShowConflicts(false);
  };

  const displayAnswer = item.final_answer || item.suggested_answer;

  return (
    <div className="rounded-lg border border-gray-200 p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-gray-400">
              Q{item.question_index + 1}
            </span>
            {item.has_conflict && (
              <Badge variant="warning">
                <AlertTriangle className="mr-1 h-3 w-3" />
                Conflict
              </Badge>
            )}
            {item.status === "accepted" && (
              <Badge variant="success">
                <Check className="mr-1 h-3 w-3" />
                Accepted
              </Badge>
            )}
            {item.status === "edited" && (
              <Badge variant="default">
                <Edit3 className="mr-1 h-3 w-3" />
                Edited
              </Badge>
            )}
            {!displayAnswer && (
              <Badge variant="destructive">No answer found</Badge>
            )}
          </div>

          <p className="mt-1 text-sm font-medium text-gray-900">
            {item.question_text}
          </p>

          {editing ? (
            <div className="mt-3">
              <textarea
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                rows={4}
              />
              <div className="mt-2 flex gap-2">
                <Button size="sm" onClick={handleSave} disabled={saving}>
                  {saving ? "Saving..." : "Save"}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setEditing(false)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            displayAnswer && (
              <p className="mt-2 text-sm text-gray-600 whitespace-pre-wrap">
                {displayAnswer}
              </p>
            )
          )}
        </div>

        {!editing && (
          <div className="flex flex-shrink-0 gap-1">
            {displayAnswer && item.status !== "accepted" && (
              <Button size="sm" variant="ghost" onClick={handleAccept}>
                <Check className="h-4 w-4" />
              </Button>
            )}
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setEditing(true)}
            >
              <Edit3 className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>

      {item.has_conflict &&
        item.conflicting_answers &&
        item.conflicting_answers.length > 0 && (
          <div className="mt-3 border-t border-gray-100 pt-3">
            <button
              onClick={() => setShowConflicts(!showConflicts)}
              className="flex items-center gap-1 text-xs font-medium text-amber-600 hover:text-amber-700"
            >
              {showConflicts ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
              {item.conflicting_answers.length} conflicting answer(s)
            </button>
            {showConflicts && (
              <div className="mt-2 space-y-2">
                {item.conflicting_answers.map((alt, idx) => (
                  <div
                    key={idx}
                    className="rounded-md bg-amber-50 p-3 text-sm"
                  >
                    <p className="text-xs font-medium text-amber-700">
                      Source: {alt.source}
                    </p>
                    <p className="mt-1 text-gray-700">{alt.text}</p>
                    <Button
                      size="sm"
                      variant="outline"
                      className="mt-2"
                      onClick={() => selectConflictingAnswer(alt.text)}
                    >
                      Use this answer
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
    </div>
  );
}
