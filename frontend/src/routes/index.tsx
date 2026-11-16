import { useEffect, useRef } from "react";
import { createFileRoute } from "@tanstack/react-router";

import { AppSidebar } from "@/components/AppSidebar";
import { ChatInput } from "@/components/ChatInput";
import { ChatMessage } from "@/components/ChatMessage";
import { useChat } from "@/hooks/useChat";

export const Route = createFileRoute("/")({
  component: ChatPage,
});

function ChatPage() {
  const { messages, isStreaming, send, clear } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  return (
    <div className="flex h-full min-h-0 w-full">
      <AppSidebar
        onPick={(q) => send(q)}
        onClear={clear}
        disabled={isStreaming}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="shrink-0 border-b border-border bg-background/80 px-6 py-5 backdrop-blur">
          <div className="mx-auto w-full max-w-3xl">
            <h1 className="text-[1.875rem] font-semibold tracking-tight text-foreground">
              NovaCell Support
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Grounded answers for data, billing, SIM/eSIM, roaming, voice, and
              account basics. For personal account details, call 611 or use the
              MyTelecom app.
            </p>
          </div>
        </header>

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4">
          <div className="mx-auto w-full max-w-3xl">
            {messages.length === 0 ? (
              <EmptyState />
            ) : (
              messages.map((m) => <ChatMessage key={m.id} message={m} />)
            )}
          </div>
        </div>

        <ChatInput onSend={send} disabled={isStreaming} />

        <footer className="shrink-0 border-t border-border bg-background px-6 py-3 text-center text-[13px] text-muted-foreground">
          Responses are generated from NovaCell's verified knowledge sources.
          Always confirm account-specific details with a live agent.
        </footer>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="mb-3 flex size-14 items-center justify-center rounded-full bg-primary text-2xl text-primary-foreground">
        📡
      </div>
      <h2 className="text-lg font-semibold text-foreground">
        Hi, I'm NovaCell's support assistant
      </h2>
      <p className="mt-1 max-w-md text-sm text-muted-foreground">
        Pick a sample question from the sidebar or ask your own. I'll answer
        using NovaCell's verified knowledge base.
      </p>
    </div>
  );
}
