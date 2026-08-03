import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { studyPlansApi } from "@/api/endpoints";
import { AppLayout } from "@/components/layout/AppLayout";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

function renderValue(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(renderValue).join("\n");
  if (value && typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value ?? "");
}

export function StudyPlanDetailPage() {
  const { planId } = useParams<{ planId: string }>();

  const { data: plan, isLoading, error } = useQuery({
    queryKey: ["study-plan", planId],
    queryFn: () => studyPlansApi.get(planId!),
    enabled: !!planId,
  });

  if (isLoading) {
    return (
      <AppLayout>
        <p className="text-muted-foreground">Loading study plan...</p>
      </AppLayout>
    );
  }

  if (error || !plan) {
    return (
      <AppLayout>
        <p className="text-destructive">Study plan not found.</p>
        <Button variant="outline" className="mt-4" asChild>
          <Link to="/plans">Back to plans</Link>
        </Button>
      </AppLayout>
    );
  }

  const notesEntries = plan.notes ? Object.entries(plan.notes) : [];
  const questions = Array.isArray(plan.test?.questions)
    ? (plan.test!.questions as Array<Record<string, unknown>>)
    : plan.test
      ? [plan.test as Record<string, unknown>]
      : [];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link to="/plans">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{plan.topic}</h1>
            <p className="text-muted-foreground">
              Created {new Date(plan.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Study Topics</CardTitle>
            <CardDescription>{plan.study_topics.length} topics to cover</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {plan.study_topics.map((topic, i) => (
                <Badge key={i} variant="secondary">
                  {topic}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {notesEntries.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Notes</CardTitle>
              <CardDescription>Detailed notes for each topic</CardDescription>
            </CardHeader>
            <CardContent>
              <Accordion type="multiple" className="w-full">
                {notesEntries.map(([key, value]) => (
                  <AccordionItem key={key} value={key}>
                    <AccordionTrigger>{key}</AccordionTrigger>
                    <AccordionContent>
                      <pre className="whitespace-pre-wrap font-sans text-sm">
                        {renderValue(value)}
                      </pre>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>
        )}

        {questions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Practice Test</CardTitle>
              <CardDescription>{questions.length} questions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {questions.map((q, i) => (
                <div key={i}>
                  {i > 0 && <Separator className="mb-6" />}
                  <p className="mb-2 font-medium">
                    {i + 1}. {String(q.question ?? q.prompt ?? renderValue(q))}
                  </p>
                  {Array.isArray(q.options) && (
                    <ul className="ml-4 list-disc space-y-1 text-sm text-muted-foreground">
                      {(q.options as string[]).map((opt, j) => (
                        <li key={j}>{opt}</li>
                      ))}
                    </ul>
                  )}
                  {q.answer != null && (
                    <p className="mt-2 text-sm text-primary">
                      Answer: {String(q.answer)}
                    </p>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
