import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import { Loader2, Plus, Send } from "lucide-react";
import { chatsApi, generateApi } from "@/api/endpoints";
import { AppLayout } from "@/components/layout/AppLayout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { useTaskPoll } from "@/hooks/useTaskPoll";
import { cn } from "@/lib/utils";

export function WorkspacePage() {
  const { chatId: paramChatId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeChatId, setActiveChatId] = useState<string | null>(paramChatId ?? null);
  const [query, setQuery] = useState("");
  const [generateTaskId, setGenerateTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: chats, isLoading: chatsLoading } = useQuery({
    queryKey: ["chats"],
    queryFn: chatsApi.list,
  });

  const { data: chat, refetch: refetchChat } = useQuery({
    queryKey: ["chat", activeChatId],
    queryFn: () => chatsApi.get(activeChatId!),
    enabled: !!activeChatId,
  });

  const { status: taskStatus, isPolling } = useTaskPoll(generateTaskId, {
    onComplete: (result) => {
      setGenerateTaskId(null);
      refetchChat();
      queryClient.invalidateQueries({ queryKey: ["study-plans"] });
      const planId = (result.result as { plan_id?: string })?.plan_id;
      if (planId) navigate(`/plans/${planId}`);
    },
    onError: (err) => {
      setError(err);
      setGenerateTaskId(null);
    },
  });

  useEffect(() => {
    if (paramChatId) setActiveChatId(paramChatId);
  }, [paramChatId]);

  const createChat = async () => {
    const response = await chatsApi.create();
    setActiveChatId(response.chat_id);
    navigate(`/workspace/${response.chat_id}`);
    queryClient.invalidateQueries({ queryKey: ["chats"] });
  };

  const handleGenerate = async () => {
    if (!activeChatId || !query.trim()) return;
    setError(null);
    try {
      const response = await generateApi.create({ query: query.trim(), chat_id: activeChatId });
      setGenerateTaskId(response.task_id);
      setQuery("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    }
  };

  return (
    <AppLayout>
      <div className="flex h-[calc(100vh-8rem)] gap-6">
        <Card className="hidden w-64 shrink-0 lg:flex lg:flex-col">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Chats</CardTitle>
              <Button variant="ghost" size="icon" onClick={createChat}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="flex-1 overflow-auto p-2">
            {chatsLoading ? (
              <p className="p-2 text-sm text-muted-foreground">Loading...</p>
            ) : (
              <div className="space-y-1">
                {chats?.chats.map((c) => (
                  <button
                    key={c.chat_id}
                    onClick={() => {
                      setActiveChatId(c.chat_id);
                      navigate(`/workspace/${c.chat_id}`);
                    }}
                    className={cn(
                      "w-full rounded-md px-3 py-2 text-left text-sm transition-colors",
                      activeChatId === c.chat_id
                        ? "bg-primary text-primary-foreground"
                        : "hover:bg-accent",
                    )}
                  >
                    <div className="truncate">Chat {c.chat_id.slice(0, 8)}</div>
                    <div className="text-xs opacity-70">{c.message_count} messages</div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="flex flex-1 flex-col">
          <CardHeader>
            <CardTitle>Workspace</CardTitle>
            <CardDescription>
              Ask a question to generate a personalized study plan from your documents
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col">
            {!activeChatId ? (
              <div className="flex flex-1 flex-col items-center justify-center gap-4">
                <p className="text-muted-foreground">Create a chat session to get started</p>
                <Button onClick={createChat}>
                  <Plus className="h-4 w-4" />
                  New chat
                </Button>
              </div>
            ) : (
              <>
                <div className="mb-4 flex-1 space-y-3 overflow-auto rounded-md border border-border p-4">
                  {!chat?.messages.length ? (
                    <p className="text-sm text-muted-foreground">
                      No messages yet. Enter a topic or question below.
                    </p>
                  ) : (
                    chat.messages.map((msg, i) => (
                      <div
                        key={i}
                        className={cn(
                          "rounded-lg px-4 py-2 text-sm",
                          msg.role === "user"
                            ? "ml-8 bg-primary text-primary-foreground"
                            : "mr-8 bg-muted",
                        )}
                      >
                        <div className="mb-1 text-xs font-medium opacity-70">
                          {String(msg.role)}
                        </div>
                        <div className="whitespace-pre-wrap">{String(msg.content ?? "")}</div>
                      </div>
                    ))
                  )}
                </div>

                {isPolling && (
                  <div className="mb-4 space-y-2">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Generating study plan...
                      <Badge variant="warning">{taskStatus}</Badge>
                    </div>
                    <Progress value={60} />
                  </div>
                )}

                {error && <p className="mb-2 text-sm text-destructive">{error}</p>}

                <div className="flex gap-2">
                  <Input
                    placeholder="e.g. Explain machine learning fundamentals"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
                    disabled={isPolling}
                  />
                  <Button onClick={handleGenerate} disabled={isPolling || !query.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
