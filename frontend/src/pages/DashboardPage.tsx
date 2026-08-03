import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { FileText, BookOpen, MessageSquare, Upload } from "lucide-react";
import { chatsApi, documentsApi, studyPlansApi } from "@/api/endpoints";
import { useAuth } from "@/auth/AuthContext";
import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function DashboardPage() {
  const { user } = useAuth();

  const { data: documents } = useQuery({
    queryKey: ["documents"],
    queryFn: documentsApi.list,
  });

  const { data: chats } = useQuery({
    queryKey: ["chats"],
    queryFn: chatsApi.list,
  });

  const { data: plans } = useQuery({
    queryKey: ["study-plans"],
    queryFn: studyPlansApi.list,
  });

  const completedDocs =
    documents?.documents.filter((d) => d.status === "completed").length ?? 0;

  const stats = [
    {
      label: "Documents",
      value: documents?.documents.length ?? 0,
      sub: `${completedDocs} indexed`,
      icon: FileText,
      to: "/documents",
    },
    {
      label: "Chat Sessions",
      value: chats?.chats.length ?? 0,
      sub: "Active workspaces",
      icon: MessageSquare,
      to: "/workspace",
    },
    {
      label: "Study Plans",
      value: plans?.plans.length ?? 0,
      sub: "Generated plans",
      icon: BookOpen,
      to: "/plans",
    },
  ];

  return (
    <AppLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {user?.username}
          </h1>
          <p className="mt-1 text-muted-foreground">
            Upload documents, generate study plans, and track your learning progress.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {stats.map(({ label, value, sub, icon: Icon, to }) => (
            <Link key={label} to={to}>
              <Card className="transition-shadow hover:shadow-md">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {label}
                  </CardTitle>
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{value}</div>
                  <p className="text-xs text-muted-foreground">{sub}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Get started</CardTitle>
            <CardDescription>Follow these steps to create your first study plan</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button asChild>
              <Link to="/documents">
                <Upload className="h-4 w-4" />
                Upload documents
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/workspace">Open workspace</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/plans">View study plans</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
