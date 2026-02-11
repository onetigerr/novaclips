const shotlist = [
  {
    "scene": "1",
    "ids": "1-2",
    "timing": "00:00:00 - 00:00:07",
    "subtitles": "Have you ever been in a chat with an AI and it feels amazing... then suddenly it forgets the most important thing you said",
    "image_prompt": "Subject: Medium shot of a young man in modern techwear sitting at a wooden cafe table, looking frustrated at a transparent holographic tablet hovering in front of him. The hologram shows a chat interface turning from blue to glitchy red. \nEnvironment: Cozy coffee shop with warm lighting, blurred background of espresso machines and plants.\nStyle Token: Arcane-series artistic style, hand-painted digital textures with visible brushstrokes, ink-trace shadows, and dramatic volumetric lighting. Modern techwear aesthetic, sleek geometric shapes, sophisticated color palette of Deep Cobalt, Electric Cyan, and Soft Amber. Stylized realism, high-contrast cinematic atmosphere, 8k resolution.",
    "reference_images": "architect_768.jpeg, sunny_768.jpeg"
  },
  {
    "scene": "2",
    "ids": "3-4",
    "timing": "00:00:07 - 00:00:13",
    "subtitles": "Like you told it make it a shortlist... and three messages later it drops a giant essay anyway",
    "image_prompt": "Subject: Isometric close-up of a futuristic chat interface floating in a void. On the left, a small amber box labeled \"CONSTRAINT: SHORTLIST\". On the right, a massive, overflowing cascade of cyan text blocks tumbling down, ignoring the constraint. \nStyle Token: Arcane-series artistic style, hand-painted digital textures, visible brushstrokes. Deep Cobalt background. Electric Cyan text blocks, Soft Amber constraints. High contrast, glowing UI elements.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "3",
    "ids": "5",
    "timing": "00:00:13 - 00:00:17",
    "subtitles": "Or you say don't mention spoilers and it casually spoils the plot",
    "image_prompt": "Subject: Isometric view of a digital warning sign glowing red with a \"NO SPOILERS\" icon. A large, heavy block of cyan text crashes down on top of it, cracking the sign. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. Dramatic lighting, red danger glow vs cyan text glow.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "4",
    "ids": "6-10",
    "timing": "00:00:17 - 00:00:32",
    "subtitles": "It's tempting to think the AI is being lazy... but most of the time it's... the context window. Here's the twist...",
    "image_prompt": "Subject: Wide isometric view of a floating digital whiteboard with a glowing slate-colored frame. The whiteboard is completely packed with glowing cyan and amber data blocks, with no empty space left. Some blocks are falling off the edge into darkness. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. Minimalist Slate frame, Electric Cyan data.",
    "reference_images": "whiteboard_768.jpeg, items_768.jpeg"
  },
  {
    "scene": "5",
    "ids": "11-13",
    "timing": "00:00:33 - 00:00:39",
    "subtitles": "your message becomes tokens... both spend the same limited budget",
    "image_prompt": "Subject: Isometric view of a translucent tactical backpack with a glowing \"capacity meter\" on the side. A stream of Amber blocks (user input) and a stream of Cyan blocks (AI output) are both flowing into the *same* main compartment, which is bulging at the seams. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. Soft Amber and Electric Cyan glowing blocks. Detailed techwear texture on the backpack.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "6",
    "ids": "14-16",
    "timing": "00:00:39 - 00:00:49",
    "subtitles": "Once you see that AI amnesia starts making a lot more sense... Tokens and context window",
    "image_prompt": "Subject: A split screen or dual-hologram view. Left side: A single glowing Cyan cube (Token). Right side: A glowing Slate frame (Window). Both are floating over a blurred tech workspace background. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. Sharp focus on the two key symbols. Cinematic lighting.",
    "reference_images": "items_768.jpeg, whiteboard_768.jpeg"
  },
  {
    "scene": "7",
    "ids": "17-20",
    "timing": "00:00:49 - 00:00:58",
    "subtitles": "First we'll talk about tokens... they're more like chunks of text the model works with",
    "image_prompt": "Subject: Close-up of hands (techwear gloves) organizing a pile of glowing cyan cubes on a workbench. The cubes have faint rune-like text fragments on them. \nEnvironment: Digital workshop with tools in background. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. Electric Cyan glow from the cubes illuminating the hands.",
    "reference_images": "items_768.jpeg, architect_768.jpeg"
  },
  {
    "scene": "8",
    "ids": "21-23",
    "timing": "00:00:59 - 00:01:05",
    "subtitles": "Second we'll talk about the context window... maximum amount of tokens the model can pay attention to",
    "image_prompt": "Subject: Isometric view of the \"Whiteboard\" floating in the void. It is empty except for a glowing frame. A spotlight sweeps across the empty surface, highlighting the limited area. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. Minimalist Slate frame with Electric Cyan glowing edges.",
    "reference_images": "whiteboard_768.jpeg"
  },
  {
    "scene": "9",
    "ids": "24-26",
    "timing": "00:01:05 - 00:01:15",
    "subtitles": "Then we'll hit the main rule... input tokens + output tokens have to fit inside one shared limit",
    "image_prompt": "Subject: Isometric view of a balance scale. On one side, a pile of Amber blocks. On the other, a pile of Cyan blocks. The scale is balanced perfectly inside a glowing circular boundary line. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. Soft Amber and Electric Cyan elements.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "10",
    "ids": "27-28",
    "timing": "00:01:15 - 00:01:20",
    "subtitles": "And finally you'll get a simple toolkit... keep the AI on track... without coding",
    "image_prompt": "Subject: Top-down view of a \"Toolkit\" being opened on a cafe table. Inside are glowing holographic tools: a summarizer icon, a scissors icon, and a checklist. \nEnvironment: Cafe table surface (wood texture). \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Realistic wood texture mixed with tech holograms.",
    "reference_images": "items_768.jpeg, sunny_768.jpeg"
  },
  {
    "scene": "11",
    "ids": "29-32",
    "timing": "00:01:21 - 00:01:33",
    "subtitles": "Let's start with tokens... the model doesn't truly see words... it sees tokens",
    "image_prompt": "Subject: A large, glowing word \"UNBELIEVABLE\" floating in the air. It shatters/splits into distinct glowing chunks (tokens): \"UN\", \"BELIEV\", \"ABLE\". \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. Electric Cyan text with particle effects.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "12",
    "ids": "33-37",
    "timing": "00:01:33 - 00:01:43",
    "subtitles": "Sometimes it's a whole word... sometimes punctuation... like three exclamation points",
    "image_prompt": "Subject: A magnified view of punctuation marks (!!!) turning into three separate, heavy glowing blocks. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. High contrast.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "13",
    "ids": "38-41",
    "timing": "00:01:43 - 00:01:52",
    "subtitles": "Imagine your sentence is a Lego build... words are big pieces, tokens are smaller pieces",
    "image_prompt": "Subject: Close-up of hands assembling a complex structure using glowing LEGO-like bricks. Some bricks are large (words), others are tiny plates (tokens). \nEnvironment: Cafe table. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Realistic environment with stylized tech elements (the blocks).",
    "reference_images": "items_768.jpeg, sunny_768.jpeg"
  },
  {
    "scene": "14",
    "ids": "42-45",
    "timing": "00:01:52 - 00:02:01",
    "subtitles": "So if you type unbelievable... it might get split... instead of one neat piece",
    "image_prompt": "Subject: Isometric view of a conveyor belt. The word \"UNBELIEVABLE\" enters on the left, passes through a scanner, and exits as multiple separate cyan blocks on the right. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Tech workshop environment. Deep Cobalt and Slate machinery.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "15",
    "ids": "46-49",
    "timing": "00:02:01 - 00:02:11",
    "subtitles": "And if you type wait what... punctuation adds extra tokens... this looks short but can be expensive",
    "image_prompt": "Subject: Split screen. Left: A short sentence \"Wait... what?!!\" with a heavy stack of token blocks above it. Right: A longer smooth sentence with fewer blocks. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Comparison layout.",
    "reference_images": "items_768.jpeg, whiteboard_768.jpeg"
  },
  {
    "scene": "16",
    "ids": "50-56",
    "timing": "00:02:11 - 00:02:31",
    "subtitles": "People use a rule of thumb... 4 characters... but it varies... don't treat it like a law of physics",
    "image_prompt": "Subject: A holographic \"Ruler\" measuring a token block. The measurement flickers and changes numbers, showing instability/variance. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Tech detailing. Glitch effects on the numbers.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "17",
    "ids": "57-58",
    "timing": "00:02:31 - 00:02:37",
    "subtitles": "Tokens are the unit the model counts... and the model has a maximum number",
    "image_prompt": "Subject: A digital counter clicking upwards rapidly, approaching a red \"MAX\" line. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Dramatic red lighting as it approaches the limit.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "18",
    "ids": "59-63",
    "timing": "00:02:38 - 00:02:50",
    "subtitles": "Context window is the amount of text... I like to call it working memory",
    "image_prompt": "Subject: A glowing brain silhouette, but instead of organic matter, it's filled with organized stacks of cyan blocks. \nStyle Token: Arcane-series artistic style, hand-painted digital textures. Deep Cobalt background. Electric Cyan brain structure.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "19",
    "ids": "64-67",
    "timing": "00:02:50 - 00:03:02",
    "subtitles": "But it's not human memory... it's more like a limited size whiteboard",
    "image_prompt": "Subject: Wide shot of a clean, modern office. A large physical whiteboard on the wall is half-full with notes. A person (Architect silhouette) is writing new notes. \nEnvironment: Modern Office. \nStyle Token: Arcane-series painterly style applied to real-world location (Office). Hand-painted digital finish. Natural lighting.",
    "reference_images": "office_768.jpeg, architect_768.jpeg"
  },
  {
    "scene": "20",
    "ids": "68-71",
    "timing": "00:03:02 - 00:03:13",
    "subtitles": "In chat the whiteboard holds the conversation so far... your messages, model's replies",
    "image_prompt": "Subject: Close-up of the whiteboard. We see different colored sticky notes (Amber for user, Cyan for AI) being arranged in chronological order. \nStyle Token: Arcane-series artistic style. Detailed texture on the notes and board.",
    "reference_images": "whiteboard_768.jpeg"
  },
  {
    "scene": "21",
    "ids": "72-76",
    "timing": "00:03:13 - 00:03:27",
    "subtitles": "What happens when it gets too long... older messages truncated... can't see it",
    "image_prompt": "Subject: Time-lapse style shot of the whiteboard. It fills up completely. As new notes are added at the bottom, a \"wiper\" automatically erases the notes at the top. \nStyle Token: Arcane-series artistic style. Motion blur effect on the wiper. Fading/ghosting of top notes.",
    "reference_images": "whiteboard_768.jpeg"
  },
  {
    "scene": "22",
    "ids": "77-82",
    "timing": "00:03:27 - 00:03:39",
    "subtitles": "Classic moment... set a rule at start... later model breaks it... rule not in window",
    "image_prompt": "Subject: Specific focus on a sticky note at the very top labeled \"RULE: NO EMOJIS\". It gets erased/wiped away. Then, a new note appears at the bottom with a smiley face. \nStyle Token: Arcane-series artistic style. Dramatic irony visualized.",
    "reference_images": "whiteboard_768.jpeg"
  },
  {
    "scene": "23",
    "ids": "83-86",
    "timing": "00:03:39 - 00:03:50",
    "subtitles": "Real constraint... processing more context takes more computation",
    "image_prompt": "Subject: Isometric view of a server rack. It starts calm (blue lights), then as more data blocks flow in, it heats up (orange/red lights) and steam vents out. \nStyle Token: Arcane-series artistic style. Tech visualization. Volumetric lighting (steam/heat).",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "24",
    "ids": "87-90",
    "timing": "00:03:50 - 00:04:02",
    "subtitles": "Some apps advertise saved memory... but model still generates based on active context",
    "image_prompt": "Subject: A \"Library\" archive in the background (dark, dim) vs a bright \"Spotlight\" area (active context). The model only looks at what is in the spotlight. \nStyle Token: Arcane-series artistic style. High contrast lighting. Deep Cobalt shadows.",
    "reference_images": "dark_768.jpeg, whiteboard_768.jpeg"
  },
  {
    "scene": "25",
    "ids": "91-95",
    "timing": "00:04:02 - 00:04:19",
    "subtitles": "Most useful idea... Context is what you type PLUS what model replies",
    "image_prompt": "Subject: The \"Backpack\" metaphor again. A clear view of the empty backpack. An Amber block (Prompt) is put in. Then a huge pile of Cyan blocks (Reply) is dumped in, filling it up instantly. \nStyle Token: Arcane-series artistic style. Simple, clear composition.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "26",
    "ids": "96-98",
    "timing": "00:04:19 - 00:04:27",
    "subtitles": "Sharing one backpack... prompt goes in... answer goes in... fixed size",
    "image_prompt": "Subject: Character (Architect) in an outdoor urban setting, struggling to zip up a tactical backpack that is overflowing with glowing blocks. \nEnvironment: Urban Park/Street. \nStyle Token: Arcane-series painterly style applied to real-world location. Character Shot #4.",
    "reference_images": "architect_768.jpeg, sunny_768.jpeg"
  },
  {
    "scene": "27",
    "ids": "99-100",
    "timing": "00:04:27 - 00:04:34",
    "subtitles": "Long answer crowds out older instructions",
    "image_prompt": "Subject: Close-up of the backpack interior (cross-section). New Cyan blocks pushing old Amber blocks out of the bottom mesh. \nStyle Token: Arcane-series artistic style. Cross-section schematic view.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "28",
    "ids": "101-104",
    "timing": "00:04:34 - 00:04:44",
    "subtitles": "Situation... big wall of text... write 2000 word response... model starts writing",
    "image_prompt": "Subject: Isometric view of a text editor. A massive block of text is pasted in. A progress bar labeled \"Context\" jumps to 80% instantly. \nStyle Token: Arcane-series artistic style. UI visualization. Animated progress bar.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "29",
    "ids": "105-107",
    "timing": "00:04:44 - 00:04:52",
    "subtitles": "More it writes, more tokens it uses... eating into same total capacity",
    "image_prompt": "Subject: The progress bar continues to fill rapidly as text generates, hitting 100% and turning red. \nStyle Token: Arcane-series artistic style. Tension building.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "30",
    "ids": "108-110",
    "timing": "00:04:52 - 00:04:59",
    "subtitles": "Model ends up in weird spot... no room to keep original instructions",
    "image_prompt": "Subject: The \"Context Window\" frame sliding down a long document. The original instructions at the top slide out of the frame and turn gray/inactive. \nStyle Token: Arcane-series artistic style. Ghosting effect on old text.",
    "reference_images": "whiteboard_768.jpeg, items_768.jpeg"
  },
  {
    "scene": "31",
    "ids": "111-114",
    "timing": "00:04:59 - 00:05:09",
    "subtitles": "Smarter move: tight outline... expand one section... managing the budget",
    "image_prompt": "Subject: Split screen comparison. Left: Chaos/Overflow. Right: A neat stack of small blocks, being handled one by one. \nStyle Token: Arcane-series artistic style. Tidy vs Messy.",
    "reference_images": "items_768.jpeg, whiteboard_768.jpeg"
  },
  {
    "scene": "32",
    "ids": "115-120",
    "timing": "00:05:09 - 00:05:19",
    "subtitles": "Food ordering analogy... order all at once vs courses... less chaos",
    "image_prompt": "Subject: Restaurant scene. One table is overflowing with dishes, mess everywhere. The next table is clean, with just one course being served. \nEnvironment: Restaurant interior. \nStyle Token: Arcane-series painterly style applied to real-world location (Restaurant). Warm lighting.",
    "reference_images": "sunny_768.jpeg, persons_768.jpeg"
  },
  {
    "scene": "33",
    "ids": "121-126",
    "timing": "00:05:20 - 00:05:35",
    "subtitles": "Why not unlimited?... More context = more work... computation increases",
    "image_prompt": "Subject: A gym scene. A weightlifter is struggling to lift a bar that has way too many plates on it. \nEnvironment: Gym interior. \nStyle Token: Arcane-series painterly style applied to real-world location (Gym). Physical strain visualization.",
    "reference_images": "persons_768.jpeg"
  },
  {
    "scene": "34",
    "ids": "127-130",
    "timing": "00:05:35 - 00:05:46",
    "subtitles": "Replies get slower... warnings... trade offs",
    "image_prompt": "Subject: Isometric UI of a chat app. A \"turtle\" icon appears next to a loading bar that is moving very slowly. \nStyle Token: Arcane-series artistic style. Humorous UI element.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "35",
    "ids": "131-135",
    "timing": "00:05:46 - 00:05:57",
    "subtitles": "Bigger window but higher cost... sometimes good enough memory with summary",
    "image_prompt": "Subject: A balance scale. One side has a \"Large Window\" icon, the other has a stack of \"Gold Coins\" (Cost). They balance out. \nStyle Token: Arcane-series artistic style. Symbolic representation.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "36",
    "ids": "136-139",
    "timing": "00:05:57 - 00:06:08",
    "subtitles": "Engineering constraint... bigger windows help but you still hit ceiling",
    "image_prompt": "Subject: Vertical camera pan up a skyscraper (representing context). Even at the top, there is a roof/ceiling. \nEnvironment: Urban exterior / abstract structure. \nStyle Token: Arcane-series artistic style. Massive scale.",
    "reference_images": "sunny_768.jpeg"
  },
  {
    "scene": "37",
    "ids": "140-144",
    "timing": "00:06:09 - 00:06:23",
    "subtitles": "What happens when you hit limit... tool refuses... drops older parts",
    "image_prompt": "Subject: Isometric view of a file cabinet. A mechanical arm tries to stuff a folder in, but the drawer is stuck. It shreds an old folder to make room. \nStyle Token: Arcane-series artistic style. Mechanical details.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "38",
    "ids": "145-149",
    "timing": "00:06:23 - 00:06:39",
    "subtitles": "Produces answer that sounds confident but ignores rules... feels like lying... can't see needs",
    "image_prompt": "Subject: The AI avatar (a glowing geometric shape) looking confident/shrugging, while blindfolded. \nStyle Token: Arcane-series artistic style. Abstract characterization (no human face).",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "39",
    "ids": "150-155",
    "timing": "00:06:40 - 00:06:55",
    "subtitles": "Diagnostic: contradicting earlier constraints... not paranoid... realistic",
    "image_prompt": "Subject: A detective looking at a clue board with red string. The string leads to a void where a clue used to be. \nEnvironment: Detective office / dim room. \nStyle Token: Arcane-series artistic style. Noir atmosphere.",
    "reference_images": "dark_768.jpeg, persons_768.jpeg"
  },
  {
    "scene": "40",
    "ids": "156-161",
    "timing": "00:06:55 - 00:07:15",
    "subtitles": "What can you do? Habits... Work in stages... outline... expand",
    "image_prompt": "Subject: The Architect at a workbench, carefully arranging tools in a neat row. \nEnvironment: Workshop / Home Office. \nSpec Ref: Character Shot #5. \nStyle Token: Arcane-series painterly style. Organized, calm atmosphere.",
    "reference_images": "architect_768.jpeg, office_768.jpeg"
  },
  {
    "scene": "41",
    "ids": "162-167",
    "timing": "00:07:15 - 00:07:32",
    "subtitles": "Compact instructions... tiny constraints block... refresh context",
    "image_prompt": "Subject: Close-up of a digital post-it note. It has a concise bulleted list. A hand pins it firmly to the frame of the whiteboard. \nStyle Token: Arcane-series artistic style. UI/Paper texture mix.",
    "reference_images": "whiteboard_768.jpeg, architect_768.jpeg"
  },
  {
    "scene": "42",
    "ids": "168-171",
    "timing": "00:07:32 - 00:07:43",
    "subtitles": "Summarize key facts... paste back... pinning notes",
    "image_prompt": "Subject: Screen recording style mockup (Arcane stylized). A user highlights text, clicks \"Summarize\", gets 5 bullets, and pastes them into a new chat. \nStyle Token: Arcane-series artistic style. Stylized UI flow.",
    "reference_images": "items_768.jpeg, whiteboard_768.jpeg"
  },
  {
    "scene": "43",
    "ids": "172-176",
    "timing": "00:07:43 - 00:07:56",
    "subtitles": "Don't paste everything... share one paragraph/scene... better results",
    "image_prompt": "Subject: A pair of scissors cutting a small, relevant section out of a large document. The rest of the document falls away. \nStyle Token: Arcane-series artistic style. Visual metaphor.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "44",
    "ids": "177-182",
    "timing": "00:07:56 - 00:08:13",
    "subtitles": "Next time AI forgets... get strategic... spending tokens in and out",
    "image_prompt": "Subject: The \"Backpack\" again, but this time neatly packed. The capacity meter is at a healthy 50% green. \nStyle Token: Arcane-series artistic style. Satisfaction/Resolution.",
    "reference_images": "items_768.jpeg"
  },
  {
    "scene": "45",
    "ids": "183-185",
    "timing": "00:08:14 - 00:08:21",
    "subtitles": "Ask for outline... keep running summary",
    "image_prompt": "Subject: A checklist on a cafe table with all items ticked off green. A steaming cup of coffee next to it. \nEnvironment: Cafe table. \nStyle Token: Arcane-series painterly style. Relaxed vibe.",
    "reference_images": "sunny_768.jpeg"
  },
  {
    "scene": "46",
    "ids": "186-191",
    "timing": "00:08:21 - 00:08:35",
    "subtitles": "Curious... biggest thing you've tried... comments... borrow ideas",
    "image_prompt": "Subject: The Architect sitting in a relaxed pose in the cafe, looking directly at the \"camera\", holding a coffee cup. \nEnvironment: Cafe. \nSpec Ref: Character Shot #6 (CTA). \nStyle Token: Arcane-series painterly style. Engaging eye contact (if possible with style). Warmth.",
    "reference_images": "architect_768.jpeg, sunny_768.jpeg"
  },
  {
    "scene": "47",
    "ids": "192-197",
    "timing": "00:08:35 - 00:08:46",
    "subtitles": "Simple explanations... subscribe... better results",
    "image_prompt": "Subject: End screen layout. A stylized \"Subscribe\" button in the center (Arcane style gold/blue). Background is a montage of the Backpack, Whiteboard, and Lego blocks. \nStyle Token: Arcane-series artistic style. Title card composition.",
    "reference_images": "items_768.jpeg, whiteboard_768.jpeg"
  }
]