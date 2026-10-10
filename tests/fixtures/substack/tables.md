# Pipe tables for the Substack converter

*Each table becomes a LaTeX array in one math block.*

A math fence comes first, so the first table takes the second id.

```math
x = 1
```

| Left | Plain | Right | Centre |
| :--- | --- | ---: | :---: |
| `a\|b *c*` | [a link](https://example.com) | **bold** and *em* | ![alt text](images/first_figure.png) |
| $ % & # _ { } \ ~ ^ | \$ \~ \* \\ | `` a`b `` | ` x ` |
| short row |
| one | two | three | four | five |
|  | [![inner](images/first_figure.png)](https://example.com) | `open | 2 * 3 |

A paragraph line
| Header only |
| --- |

| Not a table, since no delimiter row follows |
| a paragraph line that opens a pipe |

| One | Two |
| --- |
| The delimiter row above has one cell for two headers, so this is a paragraph |

| Ends at a line |
| --- |
| that opens a pipe |
and this line, which does not, starts a paragraph.

<!-- markdownlint-disable-file MD038 MD055 MD056 MD058 MD060 -->
