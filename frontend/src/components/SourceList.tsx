import { useState } from "react";
import { ChevronDown } from "lucide-react";

import { cn } from "@/lib/utils";
import type { SourceDoc } from "@/hooks/useChat";

const TAG_STYLES: Record<string, string> = {
  FAQ: "bg-[var(--tag-faq-bg)] text-[var(--tag-faq-fg)]",
  TICKET: "bg-[var(--tag-ticket-bg)] text-[var(--tag-ticket-fg)]",
  GUIDE: "bg-[var(--tag-guide-bg)] text-[var(--tag-guide-fg)]",
};

interface Props {
  docs: SourceDoc[];
}

export function SourceList({ docs }: Props) {
  const [open, setOpen] = useState(false);
  if (!docs?.length) return null;

  return (
    <div className="mt-2.5 rounded-xl border border-border bg-card">
      <button
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center justify-between px-4 py-2.5 text-sm font-medium text-foreground hover:text-primary"
      >
        <span>Sources ({docs.length})</span>
        <ChevronDown
          className={cn(
            "size-4 transition-transform",
            open && "rotate-180",
          )}
        />
      </button>
      {open && (
        <div className="space-y-2 border-t border-border p-3">
          {docs.map((d, i) => {
            const tagCls =
              TAG_STYLES[d.source?.toUpperCase?.()] ?? TAG_STYLES.GUIDE;
            return (
              <div
                key={`${d.source}-${d.source_id}-${i}`}
                className="rounded-[10px] border border-border bg-background px-3 py-2.5"
              >
                <div className="mb-1 flex items-center gap-2">
                  <span
                    className={cn(
                      "inline-block rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.06em]",
                      tagCls,
                    )}
                  >
                    {d.source}
                  </span>
                  <span className="text-xs font-medium text-muted-foreground">
                    {d.source_id}
                  </span>
                  {typeof d.relevance_score === "number" && (
                    <span className="ml-auto text-xs text-muted-foreground">
                      score {d.relevance_score}
                    </span>
                  )}
                </div>
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                  {d.content}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
