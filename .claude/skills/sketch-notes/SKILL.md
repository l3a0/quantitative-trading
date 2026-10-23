---
name: sketch-notes
description: Draw a whiteboard sketch for a blog post, an animated GIF drawn stroke by stroke that sits right after the passage it explains, then show it to the owner, place it, test it, sync it and review it. Use when asked for a sketch, a sketch note, a whiteboard or an animation that makes a passage of a post easier to understand, or to slow down, redraw, recolour or fix one that exists. Not for a static chart, which a post's `chan.*_figures` module draws.
---

# Draw a whiteboard sketch

A post here explains rules, bugs and statistics in a few sentences each. A
reader who has not met the terms gets more from a picture of what happens than
from the terms, so a post can carry whiteboard sketches: short animated GIFs,
drawn stroke by stroke as if on a whiteboard, each placed right after the text
it draws. The owner calls them sketch notes.

A sketch is code, not an image file. Its strokes, labels and numbers live in a
Python module, a test pins what it draws, and the GIF in `docs/figures/` is that
module's output. That is what lets a figure in a sketch be checked against the
run it came from, and what lets a redraw prove the committed GIF is current.

## Where the machinery lives

The drawing primitives are in `chan.usdcad_tests_whiteboard`, and every post's
sketch module imports them.

| Name | What it is |
| --- | --- |
| `Stroke` | a line revealed over `frames` frames, or with `dots=` a row of dots with no line |
| `Fill` | a flat tint behind every stroke, shown whole on one frame |
| `Label` | text that appears at its place in the steps, after the stroke or tint it `names` |
| `Scene` | a title, a slug that names the GIF, and its steps in drawing order |
| `timeline`, `render` | the frames and their durations, and the images |
| `clearances` | how far each label and the title sit from the nearest ink, in pixels |
| `_line`, `_curve`, `_arrow`, `_box`, `_span`, `_check`, `_hatched` | shapes as point arrays |
| `_stroke`, `_dot` | a `Stroke` from a shape, and a one-point dot drawn in one frame |

The board is 10 units across and 4.7 up, drawn at 680 by 320 pixels. The inks
come from `chan.regime_figure`, and each keeps its meaning from sketch to
sketch.

| Ink | Meaning |
| --- | --- |
| `INK`, black | the main drawing |
| `MUTED`, grey | context, axes and notes |
| `GOOD`, green | bought, positive, the side that wins, or a value that checks out |
| `LOST`, red | shorted, negative, the side that loses, or a warning, a refusal or a zone that rejects |
| `ACCENT`, brass, which posts call brown | the one series or idea the sketch points at |

Each post gets its own module and its own test module, both named for the post,
such as `chan.usdcad_tests_whiteboard` and `tests/test_usdcad_tests_whiteboard.py`.
Each module sets a `GIF_PREFIX` that every one of its GIFs starts with. Copy
both files' shape from the newest post rather than starting from nothing. The
test module carries the shared tests listed below, and they apply to a new
post's sketches only once they are copied. `chan.equity_seasonals_whiteboard`,
which arrives with [PR #618](https://github.com/l3a0/quantitative-trading/pull/618), adds a `PACED` list of slower
sketches, a `sketch_timeline` that paces them, `_write` that saves one GIF, and
a `main` that redraws every GIF the post embeds. Until it lands, `main` has no
`PACED` list, and a slow sketch on another post adds one the same way.

An edit to `chan.usdcad_tests_whiteboard` itself changes how every post's GIFs
draw, so it is followed by a redraw of every post's sketches, not only the one
being worked on.

## The loop

Every sketch goes through the same seven steps, and the owner sees the drawing
before any test exists.

1. **Propose.** Name what each sketch would draw, one idea per sketch, and the
   paragraph it would follow. List the options in the closing message, never
   only before a tool call, and wait for a choice.
2. **Draft in a scratch folder.** Write the scene in the post's module, or in a
   scratch file while it is rough, and draw it with the script beside this
   file:

   ```bash
   uv run python .claude/skills/sketch-notes/draft.py chan.usdcad_tests_whiteboard:_adf --out <scratch>
   ```

   It writes the GIF and its last frame into the scratch folder, and refuses
   any folder inside `docs/figures`. It prints every rule the scene breaks, in
   the hand font and in the fallback font, or `ok`, and exits 1 when anything
   is broken. `tests/test_sketch_draft.py` holds each of its checks. Fix the
   scene until it prints `ok`, and look at the last frame yourself before
   sending anything.
3. **Show it, and wait.** Send the GIF to the owner, with `SendUserFile` where
   the session has it and as a path in the closing message where it does not.
   Say in a sentence what each part draws, and ask whether it works. Iterate on
   the owner's words. A sketch the owner calls too fast goes in the module's
   `PACED` list, which `--paced` previews: each label and tint shows 900 ms
   instead of 350, and the finished drawing holds 12 seconds instead of 4.
4. **Place it.** Embed the GIF right after the paragraph it draws. A section
   holding several sketches uses headings rather than a numbered list, so each
   sketch can sit beside its own text. Write the alt text from the last frame:
   the title in curly quotes, every label quoted, the drawing order as the
   frames show it, and the hold time when the sketch is paced.
5. **Pin it.** Add the scene to the module's scene list and the GIF to the
   test module's list of GIFs, then write the tests below. Redraw with the
   module's `main`, and look at `git status` on `docs/figures`. A redraw that
   changes a GIF nobody touched means a stale generator or a different machine,
   so find out which before committing. Run the figure-embed sweep in
   `CLAUDE.md`, which resolves every embedded GIF to a file that exists.
6. **Commit, push, open the pull request and sync, before the full suite.**
   Commit the GIFs and the post first, so the owner sees them sooner, and run
   the full suite in the background after. A new branch opens its pull request
   at once and sends the owner its link. Its body writes `Part of #NN` for the
   post's pre-publish tracking issue. Then the `sync-substack` skill uploads
   each new or changed GIF from the pushed commit and syncs the draft. A post
   that is published or scheduled is the exception: any change to it waits for
   the owner.
7. **Review.** Two lenses, run as independent subagents.
   - **Accuracy:** the last frame against the alt text, the code, and the run
     that gives the figures.
   - **Completeness, over-reach and test strength:** every surface that counts
     or lists the sketches, anything changed past what the sketch needed, and
     mutations of the drawing code and the post.

   Verify each finding before acting on it. Post the review on the pull
   request under `## Review`, and the cost on the tracking issue with the
   `loop-cost` skill.

## What a sketch's tests hold

A post's test module holds the rules every sketch shares, once the scene is in
its list.

- Labels clear every stroke and tint by 10 pixels in the hand font and in the
  fallback font, sit 5 pixels inside the board, and stay 4 pixels apart.
- Every label names a stroke or tint drawn before it. No label is parsed as
  math unless it is written as a formula, such as the USD.CAD post's Hurst
  exponent.
- Every stroke has at least as many points as frames.
- A pale tint that carries meaning gets a green edge. `TINT` stands 1.29 to 1
  against the white board, under WCAG 2.1's 3 to 1 for a graphical object,
  and `GOOD` stands 4.86 to 1. The equity seasonals module's `_tinted` draws
  both, and `test_every_pale_tint_has_a_green_edge` holds every tint to it.
  The published USD.CAD post's sketches keep their unedged tints until the
  owner rules on changing a live post.
- Colour is never the only cue. Green and red look alike to a reader with
  red-green colour blindness, so each group a colour marks also carries its
  own label, sign or position, and a caption names the mark it explains.
- Each GIF is 680 by 320, loops, opens on its title, holds its drawing, stays
  under 1 MB, and two draws give the same bytes.
- The committed GIF is a fresh draw, byte for byte. That test runs only on
  Darwin arm64 drawing in Comic Sans MS, the machine the GIFs are drawn on,
  and skips everywhere else, CI included. A drawing change can pass CI and
  still fail on the owner's Mac.

Each new sketch needs its own tests for what it claims.

1. **Its words.** The exact list of labels, in order.
2. **Its colours.** Each stroke and label in the ink its meaning calls for.
3. **Its geometry.** Where the meaning depends on position, assert it. A mark
   drawn to scale sits at an affine function of its value. A dot meant to sit
   beside a bar sits a fixed offset away from it.
4. **Its numbers.** A figure a sketch draws is read from the run, never typed
   into the scene. Where the run reads a committed vintage, the test can read
   the run itself, as the USD.CAD tests do. Where it needs the owner's archive,
   the figures go in a frozen dataclass. The test module pins that dataclass's
   values, and one test in the run's own module holds that the run gives them,
   so the sketch tests run without the archive. Test a second, made-up set of
   figures too, so a title or colour that should follow the data does.
5. **Its place.** A test that each GIF follows the paragraph it draws, keyed
   on that paragraph's opening words.
6. **Its alt text.** The alt text quotes every label and states what the
   picture shows, such as which bars sit wholly below zero.

Mutate each new test's target once and confirm the test fails.

## Mistakes a sketch here has made once

- **A stroke needs more points than frames.** With as many or fewer, two frames
  show the same picture, the GIF writer merges them, and the GIF's timing
  drifts from the timeline. Add points with `_line`'s `per_unit`, or lower
  `frames`. A one-point dot needs `frames=1`, which `_dot` sets. The shared
  tests allow as many points as frames, so the draft script is the stricter
  check here.
- **A label appears at its place in the steps.** Its `names` only has to point
  at a stroke or tint earlier in the steps. A label meant to close the sketch
  goes last in the steps, and the alt text follows the order the frames show.
- **A dot hides a short mark.** A marker drawn on a short bar covers it. Set it
  beside the bar at a fixed offset, and test the offset.
- **A label sitting on a line fails only in one font.** Check both fonts, as
  the draft script does.
- **A count belongs to the data.** A title that counts what it draws, such as
  "Eighteen Januaries", reads its count from the data and spells it in words.
- **Say whether a sketch is schematic.** A schematic sketch carries no figures.
  Its module docstring and README must say so, or a reader takes its shapes for
  data.

## Surfaces that move with a sketch

A new or removed sketch changes counts and lists in several places, and a
review finds whichever one was missed.

1. The sketch module's docstring, which lists its scenes and counts them.
2. The test module's `GIFS` list, and its docstring. The check that
   `docs/figures` holds exactly the GIFs the modules draw, in
   `tests/test_equity_seasonals_whiteboard.py`, reads `GIFS` from every
   `tests/test_*_whiteboard.py` it finds. So a new post's test module must be
   named that way and must define `GIFS`, and nothing else names it.
3. README's list of sketches and its counts, including the list of paced
   sketches.
4. The replication log entry's paragraph on its sketches.
5. The post's alt text, and the Substack draft through `sync-substack`.

Sweep for the old count in words and in digits before committing.
