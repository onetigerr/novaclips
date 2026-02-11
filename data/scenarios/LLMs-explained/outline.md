<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Speak English.

You are a professional scriptwriter for educational YouTube videos.

Create a detailed outline for a 10-minute video (~1500 words).

NICHE: LLMs explained
TOPIC: Tokens and context window. Main idea: context is input + output in tokens, and this is a real computational constraint.
AUDIENCE: Ages 14–25 (plus curious adults). Non‑technical viewers who use ChatGPT‑like tools but don’t code and don’t know ML jargon.

Required structure:

1. Hook (0:00-0:30) — Grab attention
2. Map (0:30-1:00) — What they'll learn
3. Main Content (1:00-8:00) — 3-5 key points
4. Takeaway (8:00-9:00) — Actionable steps
5. CTA (9:00-10:00) — Subscribe prompt

For each section provide:

- Key points (3-5 bullets)
- Suggested visual type
- Estimated duration

IMPORTANT:

- Mark any historical facts with [VERIFY]
- Mark any statistics/numbers with [SOURCE NEEDED]
- Do NOT invent specific dates, percentages, or attributions

Here’s a detailed, time-coded outline you can read like a script blueprint (built for a ~10-minute, ~1500-word video).

### 1) Hook (0:00–0:30)

Estimated duration: $30$ seconds

Suggested visual type: Fast-paced UI reenactment + animated “meter” overlay

Key points (3–5)

- Open with a familiar moment: “Why did the AI forget what I said two minutes ago?” Show a chat where the model suddenly contradicts earlier info
- Reveal the twist: it’s not “being dumb,” it’s hitting a context limit—a hard computational constraint
- Tease the big idea: “Every message you send and every word it replies costs tokens, and you’re spending from the same budget”
- Promise a payoff: viewers will learn how to stop losing important details and get better answers with simple prompt habits


### 2) Map (0:30–1:00)

Estimated duration: $30$ seconds

Suggested visual type: Roadmap graphic with 4 icons (tokens, window, meter, toolbox)

Key points (3–5)

- Define “token” in plain English: small chunks of text the model reads and writes (not the same as words)
- Explain “context window”: the maximum tokens the model can hold at once
- Clarify the key rule: context = input tokens + output tokens (your prompt plus its reply share one limit)
- Show what’s coming: 3–5 practical insights plus a quick toolkit to avoid “AI amnesia”


### 3) Main Content (1:00–8:00)

Estimated duration: $7$ minutes

Suggested visual type: Simple animations, “token budget” progress bar, on-screen chat examples, split-screen “good vs bad prompts”

#### Key point 1 (1:00–2:30): Tokens are not words

Suggested visual type: Words snapping into “LEGO pieces,” with a counter ticking up

Key points (3–5)

- Plain definition: a token is a bite-sized piece of text (could be a whole word, part of a word, punctuation, or even bits of an emoji)
- Why this matters: you can’t reliably “eyeball” how long something is just by counting words
- Quick example idea (no exact counts): show the word “unbelievable” splitting into smaller chunks, then show “ChatGPT!!!” generating extra chunks for punctuation
- Mention a common rule of thumb carefully: “People often estimate tokens as roughly ~4 characters in English” [SOURCE NEEDED], but emphasize it varies by language, spacing, and formatting

Mini beat / line you can use:

- “Tokens are how the model ‘sees’ text. If words are like sentences, tokens are like the syllables and punctuation the model actually handles.”


#### Key point 2 (2:30–4:15): Context window = the model’s working memory (and it has a ceiling)

Suggested visual type: Whiteboard filling up; older notes erased when space runs out

Key points (3–5)

- Define context window: the maximum amount of text (in tokens) the model can consider at one time
- Key concept: it’s a real limit tied to compute and memory—models can’t hold infinite conversation history “in their head” at once
- Explain “why forgetting happens”: when the conversation gets too long, older parts may be truncated (dropped) or compressed, so the model stops seeing them
- Make it tangible: show a “window frame” moving over a long conversation; what’s outside the frame doesn’t exist to the model in that moment

Optional clarification (keep non-technical):

- “Some tools have extra features like ‘memory’ or external notes, but the chat response still depends on what fits in the context window right now.”


#### Key point 3 (4:15–6:00): The big rule—context is input + output, and you pay for both

Suggested visual type: A single progress bar labeled “Token Budget,” split into “Your message” and “Model reply”

Key points (3–5)

- Say it plainly: every turn has two costs—what you send in, and what the model sends out
- Show the surprise: asking for a huge answer leaves less room for the model to “remember” earlier details because the output also consumes the window
- Demonstrate with an on-screen scenario: same prompt, two versions—(A) “Write a 2,000-word essay” vs (B) “Give a 10-bullet outline first”—and show the budget bar draining slower in version B
- Important consequence: longer replies can push earlier instructions out of view, causing the model to ignore rules you set at the start

A simple phrase for the audience:

- “It’s like a backpack: your prompt is what you pack in, and the model’s reply is more stuff you try to cram in. The backpack size doesn’t change mid-hike.”


#### Key point 4 (6:00–7:15): Bigger context usually means more compute (and often more cost/latency)

Suggested visual type: “More text → more work” conveyor belt animation; stopwatch icon

Key points (3–5)

- Intuition: the more text the model must consider, the more computation it does to produce each next token
- What users notice: longer chats can feel slower, and the tool may encourage shorter inputs or summarize older messages
- Keep it non-specific: “Different models offer different window sizes and performance tradeoffs” (avoid naming exact token limits unless you can cite them)
- Tie back to the theme: this isn’t just a design choice; it’s a practical engineering constraint

If you want one grounded, non-numeric line:

- “More context can improve accuracy—until it becomes too expensive or too slow to process.”


#### Key point 5 (7:15–8:00): What actually happens when you exceed the window

Suggested visual type: A “cut line” slicing off the top of a chat log; warning icon “context limit”

Key points (3–5)

- Common behaviors: the system may drop older messages, refuse the request, or produce a reply that misses earlier constraints
- Why it feels random: the model can sound confident even when key info fell out of the window
- A quick diagnostic: “If it starts contradicting your earlier rules, assume it can’t see them anymore”
- Set up the next section: “So how do you work with the limit instead of fighting it?”


### 4) Takeaway (8:00–9:00)

Estimated duration: $60$ seconds

Suggested visual type: On-screen checklist + “before/after” prompt makeover

Key points (3–5)

- Use a “token-smart” workflow: ask for an outline first, then expand one section at a time (keeps output smaller per turn)
- Keep instructions compact: move rules into a short “Constraints” block (e.g., tone, format, must-includes) and remove filler
- Summarize and pin context: every few turns, ask the model to create a 5–8 bullet “working memory” summary you can paste forward (you provide the summary back so it stays in view)
- Chunk big inputs: paste only the relevant excerpt, not the entire document; if needed, do multiple passes (summary → extract facts → generate final)

One quick illustrated example you can show:

- “Bad: Here’s my entire 20-page doc, rewrite everything.”
- “Better: Here are the 12 lines that matter. Keep these facts. Rewrite section 2 in 150 words.”


### 5) CTA (9:00–10:00)

Estimated duration: $60$ seconds

Suggested visual type: Creator on camera + animated subscribe button + end screen with two video cards

Key points (3–5)

- Invite action: “Next time the AI ‘forgets,’ check your token budget—your input plus its output is the hidden limit”
- Ask viewers to comment: “Have you ever hit a context limit? What were you trying to do?”
- Subscribe pitch: “If you want simple explanations of how LLM tools actually work—tokens, hallucinations, prompting, and practical workflows—subscribe”
- Tease the next episode: “Next video: why models hallucinate and how to catch it early” (no dates or performance claims)

If you’d like, I can turn this outline into a full word-for-word script with dialogue, exact on-screen text, and shot-by-shot directions—do you want the tone more playful (Gen Z) or more documentary (curious adult)?

