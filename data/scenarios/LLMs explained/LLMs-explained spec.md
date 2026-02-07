# YouTube Video Specification: "Why AI Forgets — Tokens & Context Window Explained"

## Project Overview

**Format:** Educational video essay  
**Duration:** 10 minutes (~1500 words spoken)  
**Target Audience:** Ages 14–25 + curious adults; non-technical ChatGPT users  
**Topic:** How tokens and context windows work in LLMs (main insight: context = input + output tokens, a real computational constraint)  
**Genre:** Educational storytelling / Video essay  
**Tone:** Clear, plain-spoken, relatable; no jargon; uses everyday analogies

---

## Content Structure

### 1. Hook (0:00–0:30) | 30 seconds

**Goal:** Grab attention with a relatable AI frustration moment

**Key Points:**
- Open with familiar scenario: AI suddenly "forgets" what you told it
- Examples: "Make it short" → gets long essay; "No spoilers" → spoils plot
- Reveal the twist: it's not stupidity, it's a space limit
- Introduce core concepts: tokens, context window, shared budget

**Narration Opening:**
> "Have you ever been in a chat with an AI, and it feels amazing… then suddenly it forgets the most important thing you said?"

**Visual Approach:**
- Fast-paced UI reenactment of chat going wrong
- Animated "meter" or "budget bar" overlay showing token usage
- Use Ken Burns effect on static chat screenshots

---

### 2. Map (0:30–1:00) | 30 seconds

**Goal:** Preview what viewers will learn

**Key Points:**
- Define "token" — chunks of text the model works with (not exactly words)
- Define "context window" — maximum tokens model can pay attention to
- The big rule: input tokens + output tokens = shared limit
- Promise: practical toolkit to keep AI "on track"

**Visual Approach:**
- Roadmap graphic with 4 icons (tokens, window, meter, toolbox)
- Smooth transitions using ink/smoke overlays between sections
- Typography animations for key terms

---

### 3. Main Content (1:00–8:00) | 7 minutes

#### Key Point 1: Tokens Are Not Words (1:00–2:30)

**Key Points:**
- Token = small chunk of text (word, part of word, punctuation)
- Can't eyeball token count by counting words
- Example: "unbelievable" splits into chunks; "Wait… what?!!" adds extra tokens
- Rule of thumb: ~4 characters per token in English (varies by language/formatting)

**Visual Approach:**
- LEGO metaphor: sentence breaking into building blocks
- Counter ticking up as text appears
- Ken Burns slow zoom on comparison examples
- Split-screen: "looks short" vs "looks long" with token counts

**Analogy Used:**
> "Imagine your sentence is a LEGO build. Words are the big pieces you notice. Tokens are the smaller pieces the model snaps together behind the scenes."

---

#### Key Point 2: Context Window = Working Memory with a Ceiling (2:30–4:15)

**Key Points:**
- Context window = max text (in tokens) model can consider at once
- Real computational limit (not bad design)
- When chat gets long, older parts get dropped
- Result: model can't follow rules it can't see anymore

**Visual Approach:**
- Whiteboard filling up; older notes erased when full
- "Window frame" sliding over long conversation
- What's outside frame = invisible to model
- Texture overlay: aged paper/parchment effect for vintage aesthetic

**Analogy Used:**
> "It's more like a limited-size whiteboard. You can write a bunch of stuff. But once it's full, you can't keep adding without erasing something."

---

#### Key Point 3: The Big Rule — Input + Output Share Same Budget (4:15–6:00)

**Key Points:**
- Context = what you type + what model replies
- Shared "backpack" metaphor
- Long answer crowds out older instructions
- Better approach: ask for outline first, expand incrementally

**Visual Approach:**
- Single progress bar labeled "Token Budget"
- Split visualization: "Your message" vs "Model reply"
- Before/after comparison: bad prompt vs good prompt
- Food ordering analogy: all courses at once vs paced courses

**Core Message:**
> "You and the model are basically sharing one backpack. Your prompt goes in. Its answer goes in the same backpack. And the backpack has a fixed size."

---

#### Key Point 4: Bigger Context = More Compute (6:00–7:15)

**Key Points:**
- More context requires more computation per token
- Users notice: slower responses, limit warnings
- Different models offer different tradeoffs (size vs speed vs cost)
- Engineering constraint, not wishful thinking

**Visual Approach:**
- "More text → more work" conveyor belt animation
- Stopwatch/loading indicators
- Scales showing tradeoffs (bigger window ↔ higher cost)

---

#### Key Point 5: What Happens When You Exceed the Window (7:15–8:00)

**Key Points:**
- Tool may refuse, silently drop old messages, or ignore earlier rules
- Model sounds confident but can't see what it needs
- Diagnostic: contradictions = constraints fell out of context

**Visual Approach:**
- "Cut line" slicing through chat log
- Warning icon overlay
- Red/alert visual treatment

---

### 4. Takeaway (8:00–9:00) | 60 seconds

**Goal:** Actionable workflow tips

**Practical Toolkit:**
1. **Work in stages** — ask for outline, then expand section by section
2. **Keep instructions compact** — use short "Constraints" blocks
3. **Refresh context on purpose** — ask for 5–8 bullet summary, paste it forward
4. **Paste only what matters** — one paragraph, one scene, not entire document

**Visual Approach:**
- On-screen checklist with animated checkmarks
- Before/after prompt makeover
- Side-by-side comparison examples

---

### 5. CTA (9:00–10:00) | 60 seconds

**Goal:** Engagement + subscribe

**Key Points:**
- Next time AI forgets, think strategically about token budget
- Ask viewers to comment: "What's the biggest thing you've tried in a single prompt?"
- Subscribe pitch: simple LLM explanations (tokens, hallucinations, reliable answers)
- Tease next video topic

**Visual Approach:**
- Creator on camera (optional)
- Animated subscribe button
- End screen with video cards

---

## Visual Style & Production Approach

### Core Aesthetic

**Style Reference:** Ukiyo-e Motion Design meets modern tech education  
**Mood:** Calm, meditative, but educational and engaging  
**Color Palette:** Warm neutrals + aged paper textures + tech blue/green accents

### Primary Animation Technique: Ken Burns Effect

**What It Is:**
- 90% of animation = slow camera movement on static images
- Techniques: gradual zoom in, zoom out, slow pan left-to-right
- Purpose: creates motion illusion, prevents "dead" static feeling

**Implementation:**
- Apply to all concept illustrations and UI mockups
- Speed: very slow (3–5 second moves)
- Can be done in CapCut, Premiere, or any basic editor

### Transitions

**Ink/Smoke Transitions:**
- Only complex graphic element needed
- Use pre-made overlay footage with alpha channel
- White/black smoke "wipes" between scenes
- Creates cohesive flow between segments

**Standard Transitions:**
- Fade for subtle shifts
- Typography fade-in synchronized with narration

### Layer Approach

**Simplified Production:**
- NO parallax (no separate moving layers)
- Images move as single planes
- Faster workflow, maintains focus on message

### Texture & Atmosphere

**Overlay Elements:**
- Aged paper texture across all visuals (creates unity)
- Subtle grain/film noise
- Occasional light leaks or vignettes for warmth

**Sound Design:**
- Background ambience matches on-screen content
- Nature sounds, gentle technology hums
- Creates "illusion of life" for static images

### Typography

**Subtitle Style:**
- Synced with narrator pacing
- Simple fade or typewriter animation
- Clear, readable sans-serif font
- Positioned to not obscure key visuals

---

## Technical Specifications

### Video Format
- **Resolution:** 1920×1080 (minimum) or 4K
- **Frame Rate:** 24fps or 30fps
- **Aspect Ratio:** 16:9 (YouTube standard)

### Audio
- **Voice-over:** Professional narrator or clear recording
- **Background Music:** Subtle, non-distracting (25–35% volume of voice)
- **Sound Effects:** Ambient layers, UI interaction sounds
- **Export:** 48kHz, stereo

### Assets Needed

**Visual Assets:**
1. Static illustrations for concepts:
   - LEGO blocks (token metaphor)
   - Whiteboard/erasure (context window)
   - Backpack (shared budget)
   - Progress bars/meters
   - Chat UI mockups

2. Icon set:
   - Tokens, window, meter, toolbox
   - Warning/alert symbols
   - Checkmarks for tips

3. Texture overlays:
   - Aged paper
   - Film grain
   - Smoke/ink transition footage

**Generation Options:**
- AI image generators (Midjourney, DALL-E) for concept art
- Stock footage for textures
- Design tools (Figma, Canva) for diagrams

---

## Production Workflow

### Pre-Production
1. **Script finalization** — ensure narration flows naturally when read aloud
2. **Visual research** — collect reference images for metaphors
3. **Storyboard** — rough sketch or written shot list (one per key beat)

### Production
1. **Voice recording** — record full narration first (easier to edit visuals to audio)
2. **Asset creation** — generate/design all illustrations and diagrams
3. **Animation** — apply Ken Burns effects to each image (2–4 seconds per shot)
4. **Assembly** — build timeline in editor synced to voice-over

### Post-Production
1. **Transitions** — add smoke/ink overlays at scene changes
2. **Typography** — animate subtitles/key terms
3. **Texture pass** — apply paper/grain overlays across entire video
4. **Sound design** — layer ambient sounds and UI effects
5. **Color grading** — warm, cohesive look
6. **Final mix** — balance voice, music, and effects

---

## Why This Production Approach Works

### Low-Budget MVP Strategy
- **Minimal animation skills required** — basic video editor sufficient
- **Focus on strong script + aesthetic** — content quality > motion complexity
- **Scalable workflow** — can upgrade visual quality without changing structure

### Audience Engagement
- **Dopamine loop** — constant new visual information synchronized with audio
- **Clear information hierarchy** — animations emphasize key moments
- **Aesthetic satisfaction** — beautiful stills + gentle motion = relaxing + educational

### Content-First Philosophy
> "Animation is deliberately sacrificed to avoid distracting from meaning. This is an MVP that looks polished through strong art direction."

---

## Key Success Metrics

**Educational Goals:**
- Viewer understands tokens ≠ words
- Viewer grasps context window limitation
- Viewer learns input + output share budget
- Viewer can apply 4 practical tips immediately

**Engagement Goals:**
- Hook retains 80%+ viewers past 30 seconds
- Average view duration >60% (6+ minutes)
- Comments show practical application attempts
- Subscribe conversion from CTA

---

## Production Notes

### Budget-Friendly Alternatives
- **No After Effects needed** — CapCut or Premiere sufficient
- **AI-generated art** — consistent style cheaper than custom illustration
- **Royalty-free assets** — smoke transitions available on Envato, Motion Array
- **Single narrator** — no need for multiple voices or on-camera presence

### Scalability Path
**V1 (MVP):** Static images + Ken Burns + smoke transitions  
**V2 (Enhanced):** Add subtle icon animations, more polished UI mockups  
**V3 (Premium):** Light 2D animation for metaphors, custom illustrations

---

## Appendix: Core Analogies Reference

| Concept | Analogy | Visual |
|---------|---------|--------|
| Tokens | LEGO pieces that snap together | Colorful blocks assembling |
| Context Window | Limited whiteboard that erases when full | Whiteboard with moving frame |
| Shared Budget | Single backpack for hike | Backpack filling up |
| Incremental Work | Ordering food in courses vs all at once | Restaurant table comparison |
| Token Cost | Character counting (≈4 chars per token) | Counter with text examples |

---

## Final Checklist Before Production

- [ ] Script read-aloud test (natural pacing, no jargon)
- [ ] All analogies tested for clarity with non-technical friend
- [ ] Visual style reference board created
- [ ] Ken Burns presets ready in editor
- [ ] Smoke transition assets downloaded
- [ ] Texture overlays prepared
- [ ] Voice-over recorded and approved
- [ ] Background music selected (YouTube Audio Library safe)
- [ ] Thumbnail concept sketched
- [ ] Video title A/B test options prepared

---

**END OF SPECIFICATION**
