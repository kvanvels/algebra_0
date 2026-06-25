# Deferred Decisions

## Subsection run-in style

Make subsection headings run-in so text starts on the same line.
Add to `master.tex` after the existing `\titleformat{\section}` block:

```latex
\titleformat{\subsection}[runin]
  {\normalfont\sffamily\bfseries}
  {\thesubsection.}{1em}{}[.]
```

`titlesec` is already loaded; this is a one-line change.
