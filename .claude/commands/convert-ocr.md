# OCR Conversion Workflow

Convert the next commented-out OCR paragraph in the current chapter tex file into proper LaTeX, following the strict one-paragraph-at-a-time discipline.

## Before starting any subsection

1. Read the memory notes file at `~/.claude/projects/-home-kvanvels-wkspc-tex-algebra-0/memory/project_prelims_ocr_notes.md` to refresh OCR patterns, LaTeX conventions, and current status.
2. Read the relevant PDF pages (reference: `~/Documents/Books/Math/Algebra/Algebra_ Chapter 0.pdf`; PDF page = book page + 23) to get the authoritative text — never trust the OCR alone.
3. Identify the next commented-out paragraph to convert.

## Per-paragraph loop

For each paragraph, in strict order:

1. **Read the PDF** for the passage — confirm what the text actually says.
2. **Edit the tex file** — replace the commented OCR block with proper LaTeX. Granularity rules:
   - One prose paragraph = one edit + one commit.
   - One environment (defn/lem/prop/thm/coro/rem/exam/exer) = one edit + one commit.
   - A proof with multiple paragraphs: `\begin{proof}` + first paragraph = one commit; each additional paragraph = one commit; the last paragraph closes with `\end{proof}`.
3. **Build check** (separate step — never chain with commit):
   `xelatex -interaction=nonstopmode master.tex 2>&1 | grep "^!"`
   No output = clean. Fix errors before committing.
4. **Commit**:
   `git add chapters/<file>.tex && git commit -m "<chapter>: convert §X.Y description"`
   Do NOT include Co-Authored-By lines.

## At each subsection break

- Re-read the memory notes.
- Update the status section in the memory notes to record which subsection was just completed and where work resumes next.

## Key conventions (from memory)

- Categories: `\mathsf{Ring}`, `\mathsf{Ab}`, `\mathsf{Grp}`, `\mathsf{Set}`, etc.
- Hom/End/Aut: `\operatorname{Hom}_{\mathsf{Ab}}(G,H)`, `\operatorname{End}_{\mathsf{Ab}}(G)`
- Chapter cross-refs: plain text `Chapter~II`, `Chapter~V` (not `\Cref` for chapters)
- Within-chapter cross-refs: `\Cref{label}` (capital C at sentence start, `\cref` elsewhere)
- Footnote numbers inline in OCR: splice into `\footnote{}` at the right location
- `\setminus` in OCR often means a prime: `a'` not `a\setminus`
- `\sim =` in OCR means `\cong`
- `?` at exercise start = `\exerused`; `\lnot` at exercise start = ¬ marker
- Proofs go *after* the environment: `\end{prop}` then `\begin{proof}...\end{proof}`
- `exam` environments use empty labels: `\begin{exam}{}{}` — cannot `\Cref` them
- Build check: `make` will fail on missing `mybib.bib` — ignore that error, use xelatex directly
