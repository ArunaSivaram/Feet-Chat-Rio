import { useCallback, useRef, useState } from "react";

export interface SourceDoc {
  source: string;
  source_id: string;
  relevance_score: number | null;
  content: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  docs?: SourceDoc[];
  question?: string;
  streaming?: boolean;
  errored?: boolean;
}

function uid() {
  return (
    Date.now().toString(36) + Math.random().toString(36).slice(2, 10)
  );
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const clear = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setMessages([]);
    setIsStreaming(false);
  }, []);

  const send = useCallback(async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || isStreaming) return;

    const userMsg: ChatMessage = {
      id: uid(),
      role: "user",
      content: trimmed,
    };
    const assistantId = uid();
    const assistantMsg: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      question: trimmed,
      streaming: true,
    };
    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
        signal: controller.signal,
      });
      if (!resp.ok || !resp.body) {
        throw new Error(`HTTP ${resp.status}`);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let sepIdx: number;
        while ((sepIdx = buffer.indexOf("\n\n")) !== -1) {
          const frame = buffer.slice(0, sepIdx);
          buffer = buffer.slice(sepIdx + 2);
          handleFrame(frame, assistantId);
        }
      }
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content:
                  m.content ||
                  "Something went wrong reaching the assistant. Please try again.",
                streaming: false,
                errored: true,
              }
            : m,
        ),
      );
    } finally {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, streaming: false } : m,
        ),
      );
      setIsStreaming(false);
      abortRef.current = null;
    }
  }, [isStreaming]);

  function handleFrame(frame: string, assistantId: string) {
    let event = "message";
    const dataLines: string[] = [];
    for (const line of frame.split("\n")) {
      if (line.startsWith("event: ")) event = line.slice(7).trim();
      else if (line.startsWith("data: ")) dataLines.push(line.slice(6));
    }
    if (dataLines.length === 0) return;
    let payload: any;
    try {
      payload = JSON.parse(dataLines.join("\n"));
    } catch {
      return;
    }

    if (event === "token" && typeof payload.text === "string") {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: m.content + payload.text }
            : m,
        ),
      );
    } else if (event === "docs" && Array.isArray(payload.docs)) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, docs: payload.docs } : m,
        ),
      );
    } else if (event === "error") {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: payload.message || "Assistant error.",
                errored: true,
              }
            : m,
        ),
      );
    }
  }

  return { messages, isStreaming, send, clear };
}

export async function submitFeedback(input: {
  message_id: string;
  question: string;
  answer: string;
  rating: "up" | "down";
}): Promise<void> {
  await fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}
