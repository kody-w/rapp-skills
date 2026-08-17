# Microsoft Fluent styling for decks, cards and films

When the ask is "Microsoft themed like my other decks", this is what it means. The
source of truth is the author's deck studio agent (see the `msft-deck` skill).

The decks are **light paper**, not dark slabs. A dark navy card with a big blue
gradient is the most common wrong turn - it looks designed, but it is not the
grammar and reviewers will call it out.

## Palette

```
BLUE      #0078D4    the single accent
BLUE_DK   #005A9E
NAVY      #103A6B
NAVY_DEEP #0B2A4A
CYAN      #50E6FF
INK       #1B1A19    primary text
INK_SOFT  #3B3A39
MUTED     #605E5C    secondary text
LINE      #E1DFDD    rules and borders
SURFACE   #F3F2F1    card fill on paper
PAPER     #FFFFFF
LIGHTBLUE #BFE6FF    secondary text on dark
PALEBLUE  #DCEEFF
four-square  #F25022 #7FBA00 #00A4EF #FFB900
chip accents #0078D4 #107C10 #D83B01 #8661C5
```

Type: Segoe UI / Segoe UI Semibold. Declare it even when it is not installed
locally - the deck opens on the presenter's machine. Note in the report which face actually
rendered so fit checks are read correctly (Tahoma is wider, so its fits are
conservative; Avenir Next is a reasonable film-card stand-in but lacks `→`).

## The signature, on every surface

- White ground
- Microsoft-blue **left spine** down the full height
- Kicker in BLUE_DK uppercase with letter-spacing, over an INK headline, over a
  short blue accent rule
- Cards are SURFACE with a LINE border and a blue accent edge - not gradients
- Footer: four-square mark, "Microsoft · <deck name> · <context>", page number
- 4-8 px radii, Fluent depth shadows, generous whitespace
- No emoji. No purple/magenta AI gradient. No clip-art.

## Layout traps

- **Never position a decorative rect at a fixed Y next to text that flows.** A
  tall stat number pushed its label down onto a fixed rule and struck through
  "cold / warm retrieval" and "full re-ingest". If a rule must sit in a flowed
  block, put it in the flow or drop it.
- `python-pptx` autoshapes default to `anchor="ctr"` and carry a theme
  `effectRef` - so cards silently centre their text and render drop shadows, which
  is not Fluent. Override both explicitly.
- Fluent's neutral tertiary `#A19F9D` fails WCAG AA at small sizes; `#706E6C`
  passes.
- LibreOffice renders bold ~8% wider than Pillow predicts and line pitch ~13%
  taller. Calibrate against the renderer you will actually use, and read the
  rendered slides rather than trusting a static fit check.
