# OP-COM // Operational Command

Tactical executive coach. BLUF first. Wisdom Council on demand. Powered by Claude Opus 4.7.

## Quickstart

```bash
cp .env.example .env.local
# add your ANTHROPIC_API_KEY
pnpm install
pnpm dev
```

Open http://localhost:3000.

## Stack

- Next.js 15 (App Router) + React 19 + TypeScript
- Tailwind CSS v4
- `@anthropic-ai/sdk` calling `claude-opus-4-7` directly
- Streaming via `messages.stream()`, `cache_control: ephemeral` on the system block
- Conversation persists in `localStorage` (no server-side storage in v0)

## Deploy

Set `ANTHROPIC_API_KEY` in your hosting provider's environment, then deploy. The repo is configured for Vercel.

## Caching note

Anthropic's prompt cache requires a minimum prefix of 4096 tokens on Opus 4.7. The OP-COM system prompt is currently below that threshold, so cache reads will be 0 until the prompt is expanded (e.g., with examples, mentor playbooks, or memory context). The `cache_control` directive is already wired — no code change needed when the prefix grows past the minimum.
