# Driving a signed-in Microsoft browser

Copilot Studio and M365 sessions are the scarcest resource in this work. The
`copilotstudio` SSO cookie is session-only, so every browser you close destroys a
sign-in the user performed by hand. Treat this as a hard rule:

> "DONT CLOSE YOUR BROWSER JUST OPEN NEW TABS SO I DONT HAVE TO KEEP DOING THIS"

## First choice: claude-in-chrome

If the extension is paired, use it. It is already in the user's authenticated session and
nothing needs to be launched. Discover selectors by reading the live DOM rather
than guessing CSS.

## When the extension is not paired: the profile clone

Chrome 136+ refuses `--remote-debugging-port` on the default profile, and a fresh
automation profile gets stuck in Microsoft's login loop. What works:

```bash
# 1. quit Chrome
osascript -e 'tell application "Google Chrome" to quit'

# 2. clone the profile (cookies decrypt because the keychain is the same)
SRC="$HOME/Library/Application Support/Google/Chrome"
DST="$HOME/.rapp-director/chrome-real-copy"
rsync -a --exclude 'Cache*' --exclude '*/Cache*' --exclude 'Code Cache' \
      --exclude 'GPUCache' --exclude 'Service Worker/CacheStorage' \
      --exclude 'GrShaderCache' --exclude 'ShaderCache' \
      --exclude 'component_crx_cache' --exclude 'Crashpad' \
      "$SRC/Local State" "$SRC/Default" "$DST/"

# 3. give the user their Chrome back
open -a "Google Chrome"

# 4. launch the automatable copy - this is the standing capture browser
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --user-data-dir="$DST" --remote-debugging-port=9222 --no-first-run \
  --window-size=1440,900 "<studio url>" &
```

Microsoft sessions carry into the copy and Studio opens signed in with zero
prompts. Attach from every script with `connect_over_cdp("http://localhost:9222")`,
work in new tabs, and never call `close()` on the context or browser - scripts
detach and exit, the window stays.

The clone restores several tabs, so **find the page by URL** rather than taking
`pages[0]`. Taking index 0 once landed a probe on an unrelated tab and produced a
confusing "the answer is missing" result that was really "wrong tab".

## When the user must act

Open the exact page in their browser (`open "<url>"`) at the moment you hand off,
and say what to click. A link buried in chat text does not surface the work; an
open tab is the to-do. Bring the window to front and play a sound if it is
time-sensitive.
