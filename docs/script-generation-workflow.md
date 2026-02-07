# Script Generation Manual Workflow

> **Goal**: Step-by-step guide for creating fact-checked 10-minute video scripts using LLM via dialogue (ChatGPT, Claude, etc.)

---

## Overview

This is a **manual workflow** — you work with an LLM in a chat interface, using copy-paste prompts. No coding required.

**Roles in the dialogue:**
1. **Author** — writes initial content
2. **Editor** — reviews and flags claims
3. You switch roles by changing prompts

---

## Content Verification Tiers

Before writing, understand the 3 content categories:

| Tier | Category | Examples | Rule |
|------|----------|----------|------|
| 🟢 **Safe** | Definitions / Mechanics | "What is RAG", "How retry works" | ✅ Keep as-is |
| 🟡 **Cautious** | History / Cases | "When X appeared", "Who invented Y" | ⚠️ Verify OR remove |
| 🔴 **Strict** | Numbers / Comparisons | "X% improvement", "Top model" | ❌ Source required OR remove |

---

## Harmful Content Rules

**NEVER include:**
- Medical / financial / legal advice
- Conspiracy theories
- Unverified claims as facts
- Misleading comparisons

---

## Step-by-Step Workflow

### Step 1: Create Outline (Author Role)

> [!TIP]
> **How to use placeholders:** 
> When you see `[YOUR ...]`, replace it with your actual data before sending the prompt.
> For example, `AUDIENCE: [YOUR AUDIENCE]` becomes `AUDIENCE: Senior Python Developers`.

**Copy this prompt into ChatGPT:**

```
You are a professional scriptwriter for educational YouTube videos.

Create a detailed outline for a 10-minute video (~1500 words).

NICHE: [YOUR NICHE]
TOPIC: [YOUR TOPIC]
AUDIENCE: [YOUR AUDIENCE]

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
- **Markers**: These are signals from the LLM to you. 
- Mark any historical facts with `[VERIFY]` (means: check if this event actually happened).
- Mark any statistics/numbers with `[SOURCE NEEDED]` (means: find a real reference for this number).
- Do NOT invent specific dates, percentages, or attributions.
```

**Your action:** Review the outline. Remove or note any claims with [VERIFY] or [SOURCE NEEDED].

---

### Step 2: Write Sections (Context-Aware)

> [!IMPORTANT]
> **Use the same chat window!** Since the LLM already knows the outline, you don't need to copy-paste it back. Just tell it which section to write.

**Prompt to send:**

```
Excellent. Now, following the outline we just created, write the FULL SPOKEN TEXT for [SECTION NUMBER, e.g., Section 1].

Requirements:
- Conversational, active voice, short sentences.
- Use the estimated duration from the outline.
- Classify claims inline: 🟢 [SAFE], 🟡 [CAUTIOUS], 🔴 [STRICT].
- List all CAUTIOUS and STRICT claims at the end of the text.
```

---

### Step 3: Review Section (Editor Role)

**Prompt to send in the same chat:**

```
Now, switch to the role of a Senior Script Editor. 
Review the text you just wrote for [SECTION NUMBER].

Check for:
1. Clarity and Flow.
2. Correctness of claim classification.
3. Harmful content (medical/financial advice, etc.).

Provide a table of claims and specific revision suggestions if needed.
```

---

### Step 4: Verify Claims

**For each 🟡 CAUTIOUS or 🔴 STRICT claim, do manual verification:**

**Option A — Use LLM to help search:**
```
Find a reliable source for this claim:
"[CLAIM TEXT]"

Acceptable sources:
- Research papers (arxiv)
- Official documentation
- Company announcements
- Established news outlets

If no source exists, suggest how to rephrase without the specific claim.
```

**Option B — Manual search:**
- Google the claim
- Check official documentation
- Find research papers

**Decision:**
- ✅ Source found → keep claim, note source
- ❌ No source → remove or rephrase as general principle

---

### Step 5: Final Review

**After all sections are verified, do final check:**

```
You are a final reviewer. Check this complete script:

[PASTE FULL SCRIPT]

Checklist:
1. [ ] Hook grabs attention in first 10 seconds?
2. [ ] Clear structure with smooth transitions?
3. [ ] All STRICT claims have sources or removed?
4. [ ] No medical/financial/legal advice?
5. [ ] Word count matches ~1500 words?
6. [ ] Script reads naturally when spoken?

Provide final recommendations.
```

---

## Quick Reference Card

| Step | Role | Action |
|------|------|--------|
| 1 | Author | Generate outline |
| 2 | Author | Write sections with claim markers |
| 3 | Editor | Review each section |
| 4 | You | Verify CAUTIOUS/STRICT claims |
| 5 | Editor | Final review |

---

## Example Claim Classification

**🟢 Safe (keep as-is):**
> "RAG combines retrieval with generation to reduce hallucinations"

**🟡 Cautious (verify or remove):**
> "The transformer architecture was introduced in 2017" 
> → Verify: Yes, "Attention Is All You Need" paper, June 2017 ✅

**🔴 Strict (source or remove):**
> "GPT-4 achieves 86% on MMLU benchmark"
> → No source? → Rephrase: "GPT-4 performs well on academic benchmarks"
