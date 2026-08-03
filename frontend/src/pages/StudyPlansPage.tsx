import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ChevronRight } from "lucide-react";
import { studyPlansApi } from "@/api/endpoints";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function StudyPlansPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["study-plans"],
    queryFn: studyPlansApi.list,
  });

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Study Plans</h1>
          <p className="text-muted-foreground">View your generated study plans and practice tests</p>
        </div>

        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : !data?.plans.length ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">No study plans yet.</p>
              <Link to="/workspace" className="mt-2 inline-block text-sm text-primary hover:underline">
                Go to workspace to generate one
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {data.plans.map((plan) => (
              <Link key={plan.id} to={`/plans/${plan.id}`}>
                <Card className="transition-shadow hover:shadow-md">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{plan.topic}</CardTitle>
                      <CardDescription>
                        {plan.study_topics.length} topics ·{" "}
                        {new Date(plan.created_at).toLocaleDateString()}
                      </CardDescription>
                    </div>
                    <ChevronRight className="h-5 w-5 text-muted-foreground" />
                  </CardHeader>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
