"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { OP_COM_INIT_LINE } from "@/lib/op-com-prompt";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const STORAGE_KEY = "op-com.transcript.v1";

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: OP_COM_INIT_LINE },
  ]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as Message[];
        if (Array.isArray(parsed) && parsed.length > 0) setMessages(parsed);
      }
    } catch {}
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch {}
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  async function send(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || streaming) return;

    setError(null);
    setInput("");

    const next: Message[] = [
      ...messages,
      { role: "user", content: text },
      { role: "assistant", content: "" },
    ];
    setMessages(next);
    setStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const apiMessages = next
        .slice(0, -1)
        .filter((m) => m.content.length > 0)
        .filter((_, i, arr) => !(i === 0 && arr[0].content === OP_COM_INIT_LINE))
        // Drop the seeded init-line so the conversation starts at the user turn
        .filter((m) => m.content !== OP_COM_INIT_LINE);

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: apiMessages }),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        const detail = await res.text().catch(() => "");
        throw new Error(`OP-COM transmission failed (${res.status}) ${detail}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setMessages((prev) => {
          const copy = prev.slice();
          const last = copy[copy.length - 1];
          if (last && last.role === "assistant") {
            copy[copy.length - 1] = {
              ...last,
              content: last.content + chunk,
            };
          }
          return copy;
        });
      }
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      setError(
        err instanceof Error ? err.message : "Unknown OP-COM transmission error",
      );
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }

  function abort() {
    abortRef.current?.abort();
    setStreaming(false);
  }

  function reset() {
    abortRef.current?.abort();
    setMessages([{ role: "assistant", content: OP_COM_INIT_LINE }]);
    setError(null);
  }

  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b border-[var(--color-edge)] bg-[var(--color-panel)] px-5 py-3">
        <div className="flex items-center gap-3">
          <div className="h-2 w-2 animate-pulse rounded-full bg-[var(--color-accent)]" />
          <div>
            <div className="text-sm font-bold tracking-[0.2em] text-[var(--color-text)]">
              OP-COM
            </div>
            <div className="text-[10px] uppercase tracking-[0.3em] text-[var(--color-muted)]">
              Operational Command // Opus 4.7
            </div>
          </div>
        </div>
        <button
          onClick={reset}
          className="rounded border border-[var(--color-edge)] px-3 py-1 text-xs uppercase tracking-widest text-[var(--color-muted)] transition hover:border-[var(--color-accent)] hover:text-[var(--color-accent)]"
        >
          New Session
        </button>
      </header>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-5">
          {messages.map((m, i) => (
            <Bubble key={i} role={m.role} content={m.content} streaming={streaming && i === messages.length - 1 && m.role === "assistant"} />
          ))}
          {error && (
            <div className="rounded border border-red-900/60 bg-red-950/40 px-4 py-3 text-sm text-red-200">
              {error}
            </div>
          )}
        </div>
      </div>

      <form
        onSubmit={send}
        className="border-t border-[var(--color-edge)] bg-[var(--color-panel)] px-5 py-4"
      >
        <div className="mx-auto flex max-w-3xl items-end gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send(e as unknown as FormEvent);
              }
            }}
            placeholder="Give me the BLUF..."
            rows={2}
            className="flex-1 resize-none rounded border border-[var(--color-edge)] bg-[var(--color-bg)] px-3 py-2 text-sm text-[var(--color-text)] outline-none transition focus:border-[var(--color-accent)]"
          />
          {streaming ? (
            <button
              type="button"
              onClick={abort}
              className="rounded border border-[var(--color-accent)] bg-[var(--color-accent)] px-4 py-2 text-xs font-bold uppercase tracking-widest text-black transition hover:opacity-80"
            >
              Halt
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim()}
              className="rounded border border-[var(--color-accent)] bg-[var(--color-accent)] px-4 py-2 text-xs font-bold uppercase tracking-widest text-black transition hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-30"
            >
              Transmit
            </button>
          )}
        </div>
        <div className="mx-auto mt-2 max-w-3xl text-[10px] uppercase tracking-[0.25em] text-[var(--color-muted)]">
          Enter to send · Shift+Enter for newline · Conversation persists locally
        </div>
      </form>
    </div>
  );
}

function Bubble({
  role,
  content,
  streaming,
}: {
  role: "user" | "assistant";
  content: string;
  streaming: boolean;
}) {
  const isUser = role === "user";
  return (
    <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
      <div className="mb-1 text-[10px] uppercase tracking-[0.3em] text-[var(--color-muted)]">
        {isUser ? "Operator" : "OP-COM"}
      </div>
      <div
        className={`max-w-[85%] whitespace-pre-wrap rounded border px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "border-[var(--color-edge)] bg-[var(--color-panel)] text-[var(--color-text)]"
            : "border-[var(--color-accent)]/40 bg-[var(--color-panel)] text-[var(--color-text)]"
        }`}
      >
        {content}
        {streaming && (
          <span className="ml-1 inline-block h-3 w-2 animate-pulse bg-[var(--color-accent)] align-middle" />
        )}
      </div>
    </div>
  );
}
