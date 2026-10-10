# A post that uses every shape the Substack converter reads

*The subtitle line costs \$5 and loses its escape, as body text does.*

This opening paragraph runs across two lines
in the source, and the converter joins them with one space.

A second paragraph mixes **bold text**, *italic text*, `inline code` and [a link](https://example.com/one). It nests marks too: **bold with `code` inside**, [a **bold** link](https://example.com/two), and *italic with [a link](https://example.com/three)*. An escaped tilde reads \~30 and an escaped dollar reads \$2.09.

## The first section

The first level-1 heading has no widget before it, because the opening section is still running.

### A level-2 heading

A display equation follows.

```math
\hat{\beta} = \frac{\sum x_t y_t}{\sum x_t^2}
```

Its source follows in a plain fence.

```latex
\hat{\beta} = \frac{\sum x_t y_t}{\sum x_t^2}
```

A second equation takes the next id.

```math
\text{cost} = 8.7\%
```

An empty fence still becomes a code block.

```text
```

#### A level-3 heading

A table becomes a third LaTeX block.

| Shape | Becomes |
| :--- | ---: |
| `table` | an array, 100% |

## The second section, after the first widget

![A figure with a caption](images/first_figure.png)

*Figure 1: the caption is the next italic line, with **bold** inside.*

[![A linked figure with no caption](images/first_figure.png)](https://example.com/five)

![A figure with no caption](images/second_figure.png)

**Bold opening text** makes this line a paragraph rather than a caption, although it *ends in an asterisk*

1. The first numbered item, with *italic* text.
   1. A nested numbered item.
   2. A second nested numbered item.
2. The second numbered item.
   - A nested bullet under a numbered item.
   - A second nested bullet.
3. The third numbered item, with no nested list.

- A bullet with `code`.
- A bullet with [a link](https://example.com/four).

## The closing section

The last paragraph comes before the closing widget.
