import { cn } from "@/lib/utils";
import type { ChatMessage as Msg } from "@/hooks/useChat";
import { FeedbackButtons } from "./FeedbackButtons";
import { SourceList } from "./SourceList";

interface Props {
  message: Msg;
}

export function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className="fade-in flex gap-3 py-3">
      <Avatar role={message.role} />
      <div className="flex-1 min-w-0">
        <div
          className={cn(
            "rounded-2xl px-4 py-3 shadow-sm",
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-card border border-border text-foreground",
          )}
        >
          {message.content ? (
            <p className="whitespace-pre-wrap text-[15px] leading-relaxed">
              {message.content}
              {message.streaming && (
                <span className="ml-0.5 inline-block w-1.5 h-4 bg-current align-[-2px] animate-pulse" />
              )}
            </p>
          ) : (
            <TypingDots />
          )}
        </div>
        {!isUser && message.docs && message.docs.length > 0 && (
          <SourceList docs={message.docs} />
        )}
        {!isUser && !message.streaming && message.content && !message.errored && (
          <FeedbackButtons
            messageId={message.id}
            question={message.question ?? ""}
            answer={message.content}
          />
        )}
      </div>
    </div>
  );
}

function Avatar({ role }: { role: "user" | "assistant" }) {
  const isUser = role === "user";
  return (
    <div
      className={cn(
        "flex size-9 shrink-0 items-center justify-center rounded-full text-base",
        isUser
          ? "bg-[var(--border)] text-foreground"
          : "bg-primary text-primary-foreground",
      )}
      aria-hidden
    >
      {isUser ? "🙂" : "📡"}
    </div>
  );
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      <span className="size-1.5 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:-0.3s]" />
      <span className="size-1.5 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:-0.15s]" />
      <span className="size-1.5 rounded-full bg-muted-foreground/60 animate-bounce" />
    </div>
  );
}
