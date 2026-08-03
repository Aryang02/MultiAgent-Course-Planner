import { useEffect, useRef, useState } from "react";
import { tasksApi } from "@/api/endpoints";
import type { TaskStatusResponse } from "@/api/types";

interface UseTaskPollOptions {
  enabled?: boolean;
  onComplete?: (result: TaskStatusResponse) => void;
  onError?: (error: string) => void;
}

export function useTaskPoll(taskId: string | null, options: UseTaskPollOptions = {}) {
  const { enabled = true, onComplete, onError } = options;
  const [status, setStatus] = useState<string | null>(null);
  const [result, setResult] = useState<TaskStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const intervalRef = useRef(2000);
  const callbacksRef = useRef({ onComplete, onError });
  callbacksRef.current = { onComplete, onError };

  useEffect(() => {
    if (!taskId || !enabled) return;

    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout>;

    const poll = async () => {
      setIsPolling(true);
      try {
        const response = await tasksApi.get(taskId);
        if (cancelled) return;

        setStatus(response.status);
        setResult(response);

        if (response.status === "completed") {
          setIsPolling(false);
          callbacksRef.current.onComplete?.(response);
          return;
        }

        if (response.status === "failed") {
          const errMsg = response.error ?? "Task failed";
          setError(errMsg);
          setIsPolling(false);
          callbacksRef.current.onError?.(errMsg);
          return;
        }

        intervalRef.current = Math.min(intervalRef.current * 1.2, 5000);
        timeoutId = setTimeout(poll, intervalRef.current);
      } catch (err) {
        if (cancelled) return;
        const errMsg = err instanceof Error ? err.message : "Polling failed";
        setError(errMsg);
        setIsPolling(false);
        callbacksRef.current.onError?.(errMsg);
      }
    };

    intervalRef.current = 2000;
    setError(null);
    setStatus("pending");
    poll();

    return () => {
      cancelled = true;
      clearTimeout(timeoutId);
    };
  }, [taskId, enabled]);

  return { status, result, error, isPolling };
}
