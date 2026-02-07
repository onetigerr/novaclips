# Full spoken narration

---

## 1) Hook (0:00–0:30)

Have you ever been in a chat with an AI, and it feels amazing… then suddenly it forgets the most important thing you said? 🟢 [SAFE]

Like, you told it, “Make it a short list.” And three messages later, it drops a giant essay anyway. 🟡 [CAUTIOUS]

Or you say, “Don’t mention spoilers.” And it casually spoils the plot. 🟡 [CAUTIOUS]

It’s tempting to think the AI is being lazy or dramatic. 🟢 [SAFE]  
But most of the time, it’s something way more boring and way more real: it ran out of space. 🟡 [CAUTIOUS]

And that “space” has a name. It’s the context window. 🟢 [SAFE]

Here’s the twist: every message you type and every message it writes back gets converted into tokens, and you’re both spending from the same limited budget. 🟡 [CAUTIOUS]

Once you see that, “AI amnesia” starts making perfect sense. 🟢 [SAFE]

## 2) Map (0:30–1:00)

In the next few minutes, I’ll make two weird words feel normal: tokens and context window. 🟢 [SAFE]

First, we’ll talk about tokens. They’re not exactly words. They’re more like chunks of text the model works with. 🟢 [SAFE]

Second, we’ll talk about the context window. That’s the maximum amount of tokens the model can pay attention to at one time. 🟢 [SAFE]

Then we’ll hit the main rule that changes how you use these tools: context equals your input tokens plus the model’s output tokens, all inside one shared limit. 🟡 [CAUTIOUS]

And finally, you’ll get a simple toolkit. You’ll learn how to keep the AI “on track,” even in long chats, without any coding or tech jargon. 🟢 [SAFE]

## 3) Main Content (1:00–8:00)

## Key point 1 (1:00–2:30): Tokens are not words

Let’s start with tokens, because this is the part nobody explains well. 🟢 [SAFE]

When you type a message, the model doesn’t truly see “words” the way you do. 🟢 [SAFE]  
It sees tokens. 🟢 [SAFE]

A token is a small chunk of text. 🟢 [SAFE]  
Sometimes it’s a whole word. 🟢 [SAFE]  
Sometimes it’s part of a word. 🟢 [SAFE]  
Sometimes it’s punctuation, like a comma, or a dash, or three exclamation points in a row. 🟢 [SAFE]

Here’s a simple way to picture it. Imagine your sentence is a LEGO build. 🟢 [SAFE]  
Words are the big pieces you notice. 🟢 [SAFE]  
Tokens are the smaller pieces the model snaps together behind the scenes. 🟢 [SAFE]

So if you type something like “unbelievable,” it might get split into a couple of chunks instead of staying as one neat piece. 🟡 [CAUTIOUS]  
And if you type “Wait… what?!!” the dots and punctuation can add extra tokens you didn’t expect. 🟡 [CAUTIOUS]

That’s why “this looks short” can still be expensive. 🟢 [SAFE]  
And “this looks long” might be cheaper than you think. 🟢 [SAFE]

People sometimes use a rough rule of thumb like “in English, tokens average around four characters.” 🟡 [CAUTIOUS]  
But don’t treat that like a law of physics. It varies a lot by language, spacing, formatting, and the exact text. 🟢 [SAFE]

The only point you need today is this: tokens are the unit the model counts. 🟢 [SAFE]  
And the model has a maximum number it can handle at once. 🟢 [SAFE]

## Key point 2 (2:30–4:15): The context window is working memory with a ceiling

Now let’s talk about that maximum. 🟢 [SAFE]

The context window is the amount of text—in tokens—that the model can consider at one time while generating its next reply. 🟢 [SAFE]

I like to call it “working memory,” but with one big warning: it’s not human memory. 🟡 [CAUTIOUS]  
It’s more like a limited-size whiteboard. 🟢 [SAFE]

You can write a bunch of stuff on the whiteboard. 🟢 [SAFE]  
But once it’s full, you can’t keep adding without erasing something. 🟢 [SAFE]

In a chat, that “whiteboard” is filled by the conversation so far: your earlier messages, the model’s earlier replies, and sometimes system instructions you don’t see. 🟡 [CAUTIOUS]

So what happens when the chat gets too long?

Often, the tool will start dropping older parts of the conversation from what the model can see. 🟡 [CAUTIOUS]  
And when the model can’t see it, it can’t reliably follow it. 🟢 [SAFE]

That’s when you get the classic moment: you set a rule at the start, like “Keep it under 100 words,” and later the model breaks it. 🟡 [CAUTIOUS]  
Not because it wants to. But because the rule might not be inside the window anymore. 🟡 [CAUTIOUS]

And yes, this is a real constraint, not just “bad design.” 🟡 [CAUTIOUS]  
Processing more context generally takes more computation and memory. 🟡 [CAUTIOUS]

One more important note: some apps advertise extra features like saved memory, profile notes, or retrieval from documents. 🟡 [CAUTIOUS]  
That can help. But the model still generates each response based on the tokens it has in context right now. 🟡 [CAUTIOUS]

## Key point 3 (4:15–6:00): The big rule—input plus output share the same budget

This is the most useful idea in the whole video, so I’m going to say it slowly. 🟢 [SAFE]

The context window is not just what you type. 🟢 [SAFE]  
It’s what you type plus what the model replies. 🟡 [CAUTIOUS]

So you and the model are basically sharing one backpack. 🟢 [SAFE]  
Your prompt goes in the backpack. 🟢 [SAFE]  
Then the model’s answer goes in the same backpack. 🟢 [SAFE]  
And the backpack has a fixed size. 🟢 [SAFE]

That means a long answer doesn’t just cost time. 🟢 [SAFE]  
It can crowd out older instructions and details. 🟡 [CAUTIOUS]

Here’s a situation you’ve probably lived.

You paste a big wall of text and say, “Read all of this and write me a detailed 2,000-word response.” 🟡 [CAUTIOUS]  
The model tries. It starts writing. 🟢 [SAFE]  
But the more it writes, the more tokens it uses. 🟢 [SAFE]  
And those output tokens are eating into the same total context capacity. 🟡 [CAUTIOUS]

So the model can end up in a weird spot where it’s generating, but it no longer has room to keep the full original instructions in view. 🟡 [CAUTIOUS]

That’s why a smarter move is often: ask for a tight outline first. 🟢 [SAFE]  
Then expand one section at a time. 🟢 [SAFE]

You’re not lowering quality. You’re managing the budget. 🟢 [SAFE]

Think of it like ordering food. 🟢 [SAFE]  
If you order everything at once, your table gets crowded and messy. 🟢 [SAFE]  
If you order in courses, you keep control. 🟢 [SAFE]

Same information. Better pacing. Less chaos. 🟢 [SAFE]

## Key point 4 (6:00–7:15): Bigger context usually means more compute (and can mean more cost and delay)

Now, why don’t we just make the context window unlimited?

Because more context usually means more work. 🟡 [CAUTIOUS]

At a high level, the model has to consider the context while choosing each next token. 🟢 [SAFE]  
So when the context grows, the computation needed per step can increase. 🟡 [CAUTIOUS]

And that can show up in ways users actually feel: responses can slow down, apps may warn you about limits, or the system might encourage shorter prompts. 🟡 [CAUTIOUS]

Also, different models can offer different context sizes, and those choices often involve tradeoffs. 🟡 [CAUTIOUS]  
Sometimes you get a bigger window but higher cost. 🟡 [CAUTIOUS]  
Sometimes you get speed but a smaller window. 🟡 [CAUTIOUS]  
And sometimes you get “good enough” memory because the app summarizes or compresses old messages. 🟡 [CAUTIOUS]

So yes, bigger context can improve results in many cases. 🟡 [CAUTIOUS]  
But it’s not free. 🟡 [CAUTIOUS]  
It’s an engineering constraint you can’t wish away. 🟡 [CAUTIOUS]

## Key point 5 (7:15–8:00): What happens when you exceed the window

Okay. What actually happens when you hit the limit?

A few common things. 🟢 [SAFE]

Sometimes the tool refuses and tells you the context is too long. 🟡 [CAUTIOUS]  
Sometimes it silently drops older parts of the chat. 🟡 [CAUTIOUS]  
Sometimes it produces an answer that sounds confident but ignores earlier rules or facts you already gave it. 🟡 [CAUTIOUS]

And that last one is the most confusing, because it feels like the model is “lying.” 🟢 [SAFE]  
But a simpler explanation is often: it can’t see what it needs anymore. 🟡 [CAUTIOUS]

Here’s a practical diagnostic you can use today: when the model starts contradicting your earlier constraints, assume those constraints fell out of context. 🟡 [CAUTIOUS]

That’s not you being paranoid. That’s you being realistic about a limited window. 🟡 [CAUTIOUS]

## 4) Takeaway (8:00–9:00)

Estimated duration: 60 seconds

Now let’s turn all of this into habits you can actually use. 🟢 [SAFE]

First: work in stages. 🟢 [SAFE]  
Ask for an outline. Then pick one section. Then expand it. 🟢 [SAFE]  
This keeps each turn smaller and easier to keep “in view.” 🟡 [CAUTIOUS]

Second: keep your instructions compact. 🟢 [SAFE]  
Instead of writing a long story about what you want, try a tiny “Constraints” block. 🟢 [SAFE]  
Like: “Tone: friendly. Format: bullets. Must include: three examples. Must avoid: spoilers.” 🟢 [SAFE]

Third: refresh the context on purpose. 🟢 [SAFE]  
Every few turns, ask the model to summarize the key facts and decisions in 5 to 8 bullets. 🟡 [CAUTIOUS]  
Then paste that summary back into the chat when you continue. 🟢 [SAFE]  
That’s like pinning the important notes onto the whiteboard so they don’t get erased. 🟢 [SAFE]

Fourth: don’t paste everything. Paste what matters. 🟢 [SAFE]  
If you’re asking about one paragraph, share one paragraph. 🟢 [SAFE]  
If you’re asking about one scene, share one scene. 🟢 [SAFE]  
You’ll usually get better results with smaller, cleaner inputs. 🟡 [CAUTIOUS]

## 5) CTA (9:00–10:00)

Estimated duration: 60 seconds

So next time an AI “forgets,” don’t just get annoyed. Get strategic. 🟢 [SAFE]

Remember the hidden rule: you’re spending tokens on the way in and on the way out, inside one fixed context window. 🟡 [CAUTIOUS]

If you want, try this the very next time you use a chat tool: ask for a short outline first, then expand one part at a time, and keep a running bullet summary you paste forward. 🟢 [SAFE]

Now I’m curious. What’s the biggest thing you’ve tried to do in a single prompt? 🟢 [SAFE]  
Was it rewriting a document? Planning a project? Studying for an exam? 🟢 [SAFE]  
Tell me in the comments, because I read them and I steal… I mean, I borrow your ideas for future videos. 🟢 [SAFE]

And if you want simple explanations of how these tools actually work—tokens, context windows, hallucinations, and how to get more reliable answers—hit subscribe. 🟢 [SAFE]  
I’ve got more videos coming that will make you instantly better at using LLMs, even if you never write a line of code. 🟡 [CAUTIOUS]

## CAUTIOUS and STRICT claims list

- “Like, you told it, ‘Make it a short list.’ And three messages later, it drops a giant essay anyway.” 🟡 [CAUTIOUS]

- “Or you say, ‘Don’t mention spoilers.’ And it casually spoils the plot.” 🟡 [CAUTIOUS]

- “But most of the time, it’s something way more boring and way more real: it ran out of space.” 🟡 [CAUTIOUS]

- “Every message you type and every message it writes back gets converted into tokens, and you’re both spending from the same limited budget.” 🟡 [CAUTIOUS]

- “Then we’ll hit the main rule… context equals your input tokens plus the model’s output tokens, all inside one shared limit.” 🟡 [CAUTIOUS]

- “So if you type something like ‘unbelievable,’ it might get split into a couple of chunks…” 🟡 [CAUTIOUS]

- “If you type ‘Wait… what?!!’ the dots and punctuation can add extra tokens you didn’t expect.” 🟡 [CAUTIOUS]

- “People sometimes use a rough rule of thumb like ‘in English, tokens average around four characters.’” 🟡 [CAUTIOUS]

- “I like to call it ‘working memory,’ but… it’s not human memory.” 🟡 [CAUTIOUS]

- “In a chat… sometimes system instructions you don’t see.” 🟡 [CAUTIOUS]

- “Often, the tool will start dropping older parts of the conversation…” 🟡 [CAUTIOUS]

- “...the rule might not be inside the window anymore.” 🟡 [CAUTIOUS]

- “And yes, this is a real constraint… Processing more context generally takes more computation and memory.” 🟡 [CAUTIOUS]

- “Some apps advertise extra features like saved memory… But the model still generates each response based on the tokens it has in context right now.” 🟡 [CAUTIOUS]

- “It’s what you type plus what the model replies.” 🟡 [CAUTIOUS]

- “...a long answer… can crowd out older instructions and details.” 🟡 [CAUTIOUS]

- “You paste a big wall of text… ‘2,000-word response.’” 🟡 [CAUTIOUS]

- “...those output tokens are eating into the same total context capacity.” 🟡 [CAUTIOUS]

- “...it no longer has room to keep the full original instructions in view.” 🟡 [CAUTIOUS]

- “Because more context usually means more work.” 🟡 [CAUTIOUS]

- “...when the context grows, the computation needed per step can increase.” 🟡 [CAUTIOUS]

- “...responses can slow down… apps may warn you… encourage shorter prompts.” 🟡 [CAUTIOUS]

- “Different models can offer different context sizes… tradeoffs.” 🟡 [CAUTIOUS]

- “Sometimes you get a bigger window but higher cost… speed but a smaller window… app summarizes…” 🟡 [CAUTIOUS]

- “Bigger context can improve results in many cases.” 🟡 [CAUTIOUS]

- “It’s an engineering constraint you can’t wish away.” 🟡 [CAUTIOUS]

- “Sometimes the tool refuses… Sometimes it silently drops older parts…” 🟡 [CAUTIOUS]

- “...it can’t see what it needs anymore.” 🟡 [CAUTIOUS]

- “When the model starts contradicting your earlier constraints, assume those constraints fell out of context.” 🟡 [CAUTIOUS]

- “That’s you being realistic about a limited window.” 🟡 [CAUTIOUS]

- “This keeps each turn smaller and easier to keep ‘in view.’” 🟡 [CAUTIOUS]

- “Ask the model to summarize… in 5 to 8 bullets.” 🟡 [CAUTIOUS]

- “You’ll usually get better results with smaller, cleaner inputs.” 🟡 [CAUTIOUS]

- “...one fixed context window.” 🟡 [CAUTIOUS]

- “I’ve got more videos coming that will make you instantly better at using LLMs…” 🟡 [CAUTIOUS]

---
