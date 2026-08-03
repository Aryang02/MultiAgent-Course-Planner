import { useCallback, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { FileUp, RefreshCw } from "lucide-react";
import { documentsApi } from "@/api/endpoints";
import { AppLayout } from "@/components/layout/AppLayout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useTaskPoll } from "@/hooks/useTaskPoll";
import { cn } from "@/lib/utils";

function statusVariant(status: string) {
  switch (status) {
    case "completed":
      return "success" as const;
    case "processing":
    case "pending":
      return "warning" as const;
    case "failed":
      return "destructive" as const;
    default:
      return "secondary" as const;
  }
}

export function DocumentsPage() {
  const queryClient = useQueryClient();
  const [uploadTaskId, setUploadTaskId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["documents"],
    queryFn: documentsApi.list,
    refetchInterval: uploadTaskId ? 3000 : false,
  });

  const { status: taskStatus, isPolling } = useTaskPoll(uploadTaskId, {
    onComplete: () => {
      setUploadTaskId(null);
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (err) => {
      setUploadError(err);
      setUploadTaskId(null);
    },
  });

  const handleUpload = useCallback(async (files: FileList | File[]) => {
    const fileArray = Array.from(files);
    if (!fileArray.length) return;

    setUploadError(null);
    try {
      const response = await documentsApi.upload(fileArray);
      setUploadTaskId(response.task_id);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    }
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      handleUpload(e.dataTransfer.files);
    },
    [handleUpload],
  );

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
            <p className="text-muted-foreground">Upload course materials for RAG-powered study plans</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Upload files</CardTitle>
            <CardDescription>Supports PDF, TXT, and DOCX files</CardDescription>
          </CardHeader>
          <CardContent>
            <div
              className={cn(
                "flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 transition-colors",
                isDragging ? "border-primary bg-accent/50" : "border-border",
              )}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={onDrop}
            >
              <FileUp className="mb-4 h-10 w-10 text-muted-foreground" />
              <p className="mb-2 text-sm font-medium">Drag and drop files here</p>
              <p className="mb-4 text-xs text-muted-foreground">or click to browse</p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.txt,.docx"
                className="hidden"
                onChange={(e) => e.target.files && handleUpload(e.target.files)}
              />
              <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                Browse files
              </Button>
            </div>

            {(isPolling || uploadTaskId) && (
              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Processing upload...</span>
                  <Badge variant="warning">{taskStatus ?? "pending"}</Badge>
                </div>
                <Progress value={taskStatus === "completed" ? 100 : 60} />
              </div>
            )}

            {uploadError && <p className="mt-2 text-sm text-destructive">{uploadError}</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Your documents</CardTitle>
            <CardDescription>{data?.documents.length ?? 0} files uploaded</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading...</p>
            ) : !data?.documents.length ? (
              <p className="text-sm text-muted-foreground">
                No documents yet. Upload your first file to get started.
              </p>
            ) : (
              <div className="divide-y divide-border">
                {data.documents.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between py-4">
                    <div>
                      <p className="font-medium">{doc.file_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(doc.uploaded_at).toLocaleString()}
                        {doc.chunk_count != null && ` · ${doc.chunk_count} chunks`}
                      </p>
                      {doc.error_message && (
                        <p className="text-xs text-destructive">{doc.error_message}</p>
                      )}
                    </div>
                    <Badge variant={statusVariant(doc.status)}>{doc.status}</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
