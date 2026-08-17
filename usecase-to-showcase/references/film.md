# Films: the contract, and the defects that shipped before frame-reading caught them

## Audio contract

- Voice `en-US-AndrewMultilingualNeural` via Azure Speech. If your Speech resources
  have `disableLocalAuth=true` (common under tenant policy), use Entra:
  `Authorization: aad#<resourceId>#<aadToken>`, token from
  `az account get-access-token --resource https://cognitiveservices.azure.com`.
- Bed `/Library/Audio/Apple Loops/Apple/01 Hip Hop/Slow Drift Ambient Synth.caf`
- `sidechaincompress=threshold=0.015:ratio=8:attack=25:release=450:makeup=1`
- `alimiter=limit=0.95`. **Never loudnorm.**
- Every VO slot mean above **-19 dB**; bed-only gaps below **-22 dB**.
- If a read does not fit its window, widen the window. Never speed up the read -
  over ~2.6 words/sec it audibly rushes.

## Cadence, measured from the reference films

The corpus average of ~2.17 w/s hides a strong internal rhythm: the open and close
breathe, the middle is dense. Budget words accordingly or the film feels rushed at
the top and airless in the demo.

| Segment | words/sec | share of all words |
|---|---|---|
| Open + problem | 1.59 | 12% |
| Overview card | 2.34 | 13% |
| Demo | 2.36 | 64% |
| Payoff + CTA | 1.89 | 12% |

## The voice-only (NOBED) variant

The presenter often wants narration with true silence between reads so they can score it
themselves. Build it in **two steps**:

1. stems → `narration.wav`, with the video **not an input at all**
2. `video + narration.wav` → output, `-map 0:v:0 -map 1:a:0`, video copied

Step 1 having no video input is the whole point. A single-command version indexed
stems as `[0:a], [1:a]...` while ffmpeg input 0 was the **video** - so the finished
film's own audio (the same narration at its own timing, plus the bed) was mixed in
as if it were a stem, and the last stem was silently dropped. The reviewer heard it
immediately as "the same voice offset at different times"; the measurements I
trusted said the mix was clean. Trust the ears.

To cut room tone, denoise and gate the **raw stem before any gain**. Gating after
the gain does nothing, because the boosted floor clears the threshold. And
`dynaudnorm` is the wrong tool here: with a high max-gain it lifts every
inter-word silence into a constant wash that reads as a second track.

Verify without subtraction (overlapping speech makes subtraction useless): sample
every window that falls **outside** the declared narration slots and assert the
peak is zero.

## Capture

- Record **tab-only** over CDP (`Page.startScreencast`). Desktop capture has
  leaked private windows three separate times - other Spaces, Mission Control, a
  non-frontmost window. Never use it.
- Drive frame capture with `wait`, not `screenshot`, when using the extension -
  both produce a frame, only one floods your context.
- Completion is "no spinner text **and** a settled body", not a length plateau.
- Turn on **End user preview** first or tool identifiers are on screen all take.

## Post

- Compress frozen spans with hard cuts. **Never motion-interpolate text** -
  `minterpolate` warps pixels along motion vectors and turns two frames of
  different text into unreadable soup.
- Reading holds are the point; spinner holds are dead time. Compress only the
  latter.

## Three defects that shipped today before frames were read

1. **Tofu boxes.** Avenir Next has no U+2192 glyph, so every "Build → Tools → ..."
   card rendered `▯`. A single-character ink test was fooled because the notdef
   box itself has ink - render the actual string and look. U+203A (`›`) renders and
   reads as a breadcrumb.
2. **A doubled narration track** - the ffmpeg input-index bug above.
3. **A claim we had not proven** - narration said the agent "answers in Microsoft
   365 Copilot" over footage of the authoring preview. If the surface was not
   exercised, the wording is "built to answer in".

## The gate

Extract frames across the whole timeline and read them. Then spawn a separate
reviewer briefed as the audience and blind to your intent. Real findings from past
runs it caught that the builder missed: internal identifiers on screen for 57 of
105 seconds, narration claiming success over a frame where the agent visibly
failed, 23 seconds held on one identical frame, the user's question never visible
despite three "ask it for..." lines.
