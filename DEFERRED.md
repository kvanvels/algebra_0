# Deferred Decisions

## intro.tex numbering-convention passage is wrong about the format

The passage in `chapters/intro.tex` explaining how cross-references
work (near "The list in brackets following an exercise...") describes
same-chapter citations as a bare `section.number` (e.g. "Remark 1.16",
"Exercise 3.1") with "in Chapter X" added separately in prose for
cross-chapter ones. That's not what `\the<counter>` actually produces:
every counter defined in `environments.tex` (`mycounter`,
`exercounter`) always renders the full `chapter.section.number` (e.g.
"Exercise 1.3.1"), confirmed from the compiled `.aux` output. So the
passage's own example is describing a format the document doesn't use.

Citations in that passage were converted to `\Cref` so they at least
track the right targets, but the prose explanation itself was left
alone (punted) rather than rewritten to match reality.

## Incorporate published errata

Aluffi maintains an errata list for *Algebra: Chapter 0* at:
<https://www.math.fsu.edu/~aluffi/algebraerrata.2016/Errata.html>

Need to go through it and apply corrections to the corresponding
chapters in this transcription.

## Subsection run-in style

Make subsection headings run-in so text starts on the same line.
Add to `master.tex` after the existing `\titleformat{\section}` block:

```latex
\titleformat{\subsection}[runin]
  {\normalfont\sffamily\bfseries}
  {\thesubsection.}{1em}{}[.]
```

`titlesec` is already loaded; this is a one-line change.
