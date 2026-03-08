"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, File, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { uploadDocuments, processAllDocuments } from "@/lib/api";

interface FileUploaderProps {
  onUploadComplete?: () => void;
}

export default function FileUploader({ onUploadComplete }: FileUploaderProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    },
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    try {
      await uploadDocuments(files, "knowledge_base");
      await processAllDocuments();
      setFiles([]);
      onUploadComplete?.();
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
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
            ? "Drop files here..."
            : "Drag & drop files here, or click to browse"}
        </p>
        <p className="mt-1 text-xs text-gray-500">
          Supports PDF, Word (.docx), and Excel (.xlsx) files
        </p>
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">
            {files.length} file(s) selected
          </p>
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between rounded-lg border border-gray-200 px-3 py-2"
            >
              <div className="flex items-center gap-2">
                <File className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-700">{file.name}</span>
                <span className="text-xs text-gray-400">
                  ({(file.size / 1024).toFixed(0)} KB)
                </span>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="text-gray-400 hover:text-red-500"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
          <Button onClick={handleUpload} disabled={uploading} className="w-full">
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Uploading & Processing...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Upload & Build Knowledge Base
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
