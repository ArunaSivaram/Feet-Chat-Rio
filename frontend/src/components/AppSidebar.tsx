import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";

const FALLBACK_SAMPLES = [
  "Why is my mobile internet so slow?",
  "How do I activate international roaming?",
  "My new SIM still shows No Service — what should I do?",
  "What are the roaming charges in the EU?",
  "How do I enable Wi-Fi calling?",
  "How do I set up AutoPay?",
];

interface Props {
  onPick: (q: string) => void;
  onClear: () => void;
  disabled?: boolean;
}

export function AppSidebar({ onPick, onClear, disabled }: Props) {
  const [samples, setSamples] = useState<string[]>(FALLBACK_SAMPLES);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/samples")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (!cancelled && data?.questions?.length) setSamples(data.questions);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <aside className="hidden md:flex md:w-72 lg:w-80 shrink-0 flex-col gap-2 border-r border-sidebar-border bg-sidebar px-4 py-6">
      <div className="text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">
        Sample questions
      </div>
      <div className="flex flex-col gap-2">
        {samples.map((q) => (
          <button
            key={q}
            onClick={() => onPick(q)}
            disabled={disabled}
            className="text-left text-sm rounded-[10px] border border-border bg-sidebar-accent px-3 py-2 text-foreground transition-colors hover:border-primary hover:text-primary disabled:cursor-not-allowed disabled:opacity-60"
          >
            {q}
          </button>
        ))}
      </div>

      <div className="mt-auto pt-6">
        <Button
          variant="ghost"
          onClick={onClear}
          disabled={disabled}
          className="w-full justify-start text-muted-foreground hover:text-destructive hover:bg-transparent"
        >
          <Trash2 className="size-4" />
          Clear conversation
        </Button>
      </div>
    </aside>
  );
}
