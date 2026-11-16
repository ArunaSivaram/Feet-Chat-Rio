import { useEffect, useRef, useState } from "react";
import { ArrowUp } from "lucide-react";

import { cn } from "@/lib/utils";

interface Props {
  onSend: (q: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled, placeholder }: Props) {
  const [value, setValue] = useState("");
  const taRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
  }, [value]);

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  }

  return (
    <div className="border-t border-border bg-background/80 px-4 py-4 backdrop-blur">
      <div className="mx-auto w-full max-w-3xl">
        <div
          className={cn(
            "flex items-end gap-2 rounded-2xl border border-border bg-card p-2 shadow-sm transition-colors",
            "focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/30",
          )}
        >
          <textarea
            ref={taRef}
            rows={1}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
            placeholder={
              placeholder ?? "Ask about data, billing, roaming, eSIM…"
            }
            disabled={disabled}
            className="min-h-[36px] max-h-[200px] flex-1 resize-none bg-transparent px-2 py-1.5 text-[15px] leading-relaxed text-foreground placeholder:text-muted-foreground focus:outline-none disabled:opacity-60"
          />
          <button
            onClick={submit}
            disabled={disabled || !value.trim()}
            aria-label="Send"
            className={cn(
              "inline-flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-colors",
              "hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed",
            )}
          >
            <ArrowUp className="size-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
