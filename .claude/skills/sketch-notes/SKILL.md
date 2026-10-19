---
name: sketch-notes
description: Draw a whiteboard sketch note for a blog post, an animated GIF drawn stroke by stroke that sits right after the passage it explains, then show it to the owner, place it, test it, sync it and review it. Use when asked for a sketch, a sketch note, a whiteboard, a visual or an animation that makes a passage of a post easier to understand, or to slow down, redraw, recolour or fix one that exists.
---

# Draw a sketch note

A post here explains rules, bugs and statistics in a few sentences each. A
reader who has not met the terms gets more from a picture of what happens than
from the terms, so a post can carry sketch notes: short animated GIFs, drawn
stroke by stroke as if on a whiteboard, each placed right after the text it
draws. The USD.CAD post carries fourteen, and the equity seasonals post
carries twenty-one on [PR #618](https://github.com/l3a0/quantitative-trading/pull/618).

A sketch is code, not an image file. Its strokes, labels and numbers live in a
Python module, a test pins what it draws, and the GIF in `docs/figures/` is that
module's output. That is what lets a figure in a sketch be checked against the
run it came from, and what lets a redraw prove the committed GIF is current.

## Where the machinery lives

The drawing primitives are in `chan.usdcad_tests_whiteboard`, and every post's
sketch module imports them.

| Name | What it is |
| --- | --- |
| `Stroke` | a line revealed over `frames` frames. One point makes a dot, and `dots=` draws a row of dots with no line |
| `Fill` | a flat tint behind every stroke, shown whole on one frame |
| `Label` | text that appears once the stroke it `names` is drawn |
| `Scene` | a title, a slug that names the GIF, and its steps in drawing order |
| `timeline`, `render` | the frames and their durations, and the images |
| `clearances` | how far each label and the title sit from the nearest ink, in pixels |
| `_line`, `_curve`, `_arrow`, `_box`, `_span`, `_check`, `_hatched`, `_stroke`, `_dot` | shapes as point arrays |

The board is 10 units across and 4.7 up, drawn at 680 by 320 pixels. The inks
come from `chan.regime_figure`, and each has one meaning across every sketch.

| Ink | Meaning |
| --- | --- |
| `INK`, black | the main drawing |
| `MUTED`, grey | context, axes and notes |
| `GOOD`, green | bought, positive, or the side that wins |
| `LOST`, red | shorted, negative, or the side that loses |
| `ACCENT`, brown | the one series or idea the sketch points at |

Each post gets its own module, named for the post, such as
`chan.usdcad_tests_whiteboard`. The equity seasonals post's
`chan.equity_seasonals_whiteboard` arrives with [PR #618](https://github.com/l3a0/quantitative-trading/pull/618) and is the
fuller example. It adds a `PACED` list of slower sketches, a `sketch_timeline` that
paces them, `_write` that saves one GIF, and a `main` that redraws every GIF the
post embeds. Copy its shape for a new post rather than starting from nothing.

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

   It writes the GIF and its last frame into the scratch folder, never into
   `docs/figures`, and prints every layout rule the scene breaks in both fonts,
   or `ok`. Fix the layout until every scene prints `ok`. Look at the last
   frame yourself before sending anything.
3. **Show it, and wait.** Send the GIF with `SendUserFile`, say in a sentence
   what each part draws, and ask whether it works. Iterate on the owner's
   words. A sketch the owner calls too fast goes in the module's `PACED` list,
   which draft with `--paced` to preview: labels show 900 ms instead of 350,
   and the finished drawing holds 12 seconds instead of 4.
4. **Place it.** Embed the GIF right after the paragraph it draws. A section
   holding several sketches uses headings rather than a numbered list, so each
   sketch can sit beside its own text. Write the alt text from the last frame:
   the title in curly quotes, every label quoted, the drawing order as the
   frames show it, and the hold time when the sketch is paced.
5. **Pin it.** Add the scene to the module's scene list and the GIF to the
   test module's list of GIFs, then write the tests below. Redraw with the
   module's `main`, and look at `git status` on `docs/figures`. A redraw that
   changes a GIF nobody touched means a stale generator or a different machine,
   so find out which before committing.
6. **Commit, push and sync before the full suite.** Commit the GIFs and the
   post first, so the owner sees them on Substack sooner, and run the full
   suite in the background after. The `sync-substack` skill uploads each new
   or changed GIF from the pushed commit and syncs the draft.
7. **Review.** Two lenses, run as independent subagents.
   - **Accuracy:** the last frame against the alt text, the code, and the run
     that gives the figures.
   - **Completeness:** every surface that counts or lists the sketches, plus
     mutations of the drawing code and the post.

   Verify each finding before acting on it. Post the review on the pull
   request under `## Review`, and the cost on the tracking issue with the
   `loop-cost` skill.

## What a sketch's tests hold

The test module for a post's sketches already holds the rules every sketch
shares, once the scene is in its list.

- Labels clear every stroke by 10 pixels in the hand font and in the fallback
  font, sit 5 pixels inside the board, and stay 4 pixels apart.
- Every label names a stroke drawn before it, and none is parsed as math.
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
4. **Its numbers.** A figure a sketch draws comes from a frozen dataclass read
   from the run, never typed into the scene. The test module pins that
   dataclass's values, and one test in the run's own module holds that the run
   gives them, so the sketch tests run without the owner's archive. Test a
   second, made-up set of figures too, so a title or colour that should follow
   the data does.
5. **Its place.** A test that each GIF follows the paragraph it draws, keyed
   on that paragraph's opening words.
6. **Its alt text.** The alt text quotes every label and states what the
   picture shows, such as which bars sit wholly below zero.

Mutate each new test's target once and confirm the test fails.

## Mistakes a sketch here has made once

- **A stroke needs more points than frames.** With fewer, two frames show the
  same picture, the GIF writer merges them, and the GIF's timing drifts from
  the timeline. Add points with `_line`'s `per_unit`, or lower `frames`.
- **A label appears with the stroke it names.** A label meant to close the
  sketch names the last stroke. The alt text follows that order, not the order
  the code lists the labels in.
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
2. The test module's GIF list, and its docstring.
3. Every test that checks the whole figures folder, such as
   `tests/test_usdcad_tests_whiteboard.py`'s check that `docs/figures` holds
   exactly the GIFs it knows. A new post's module joins that check.
4. README's list of sketches and its counts, including the list of paced
   sketches.
5. The replication log entry's paragraph on its sketches.
6. The post's alt text, and the Substack draft through `sync-substack`.

Sweep for the old count in words and in digits before committing.
