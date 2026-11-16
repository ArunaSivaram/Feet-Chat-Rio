import { useState } from "react";
import { ThumbsDown, ThumbsUp } from "lucide-react";

import { cn } from "@/lib/utils";
import { submitFeedback } from "@/hooks/useChat";

interface Props {
  messageId: string;
  question: string;
  answer: string;
}

export function FeedbackButtons({ messageId, question, answer }: Props) {
  const [rating, setRating] = useState<"up" | "down" | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleClick(value: "up" | "down") {
    if (rating || submitting) return;
    setSubmitting(true);
    try {
      await submitFeedback({
        message_id: messageId,
        question,
        answer,
        rating: value,
      });
      setRating(value);
    } finally {
      setSubmitting(false);
    }
  }

  if (rating) {
    return (
      <div className="mt-2 text-xs text-muted-foreground">
        Feedback recorded: {rating === "up" ? "👍" : "👎"}
      </div>
    );
  }

  return (
    <div className="mt-2 flex items-center gap-1.5">
      <button
        aria-label="Thumbs up"
        onClick={() => handleClick("up")}
        disabled={submitting}
        className={cn(
          "inline-flex size-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-primary disabled:opacity-50",
        )}
      >
        <ThumbsUp className="size-4" />
      </button>
      <button
        aria-label="Thumbs down"
        onClick={() => handleClick("down")}
        disabled={submitting}
        className={cn(
          "inline-flex size-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-destructive disabled:opacity-50",
        )}
      >
        <ThumbsDown className="size-4" />
      </button>
    </div>
  );
}
