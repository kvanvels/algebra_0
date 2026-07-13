LUALATEX = lualatex -file-line-error -interaction=nonstopmode -synctex=1
PDFLATEX = pdflatex -file-line-error -interaction=nonstopmode -synctex=1
MASTER   = master
FASTMASTER = master_fastcheck

.PHONY: pdf quick check_syntax check_fast clean chktex warnings

pdf: $(MASTER).pdf

# Reruns lualatex until the log stops asking for another pass (or a
# safety cap of 6 total lualatex runs is hit). A fixed 3-pass count
# was not always enough for this document: tcolorbox's breakable boxes
# can shift page-dependent label positions across passes, so 3 passes
# sometimes still left genuine undefined-reference warnings even
# though every label existed. Confirmed empirically (2026-07-09) that
# this document needs up to 5 lualatex passes after biber to reach a
# stable, fully-resolved fixed point.
$(MASTER).pdf: $(MASTER).tex $(wildcard *.tex) $(wildcard chapters/*.tex)
	-$(LUALATEX) $(MASTER)
	-biber $(MASTER)
	-makeindex $(MASTER).idx
	-$(LUALATEX) $(MASTER)
	-for i in 1 2 3 4; do \
		grep -qE "Rerun to get|may have changed" $(MASTER).log || break; \
		$(LUALATEX) $(MASTER); \
	done

quick:
	$(LUALATEX) $(MASTER)

# Fast pass with no PDF output, for catching errors/undefined refs
# without paying for font loading and page output.
check_syntax:
	$(LUALATEX) --draftmode $(MASTER)

# Much faster reference/syntax-only check: plain pdflatex (no OpenType
# font loading) against master_fastcheck.tex, which swaps in
# fonts_fast.tex (no fontspec/unicode-math) and environments_fast.tex
# (plain-text theorem environments instead of tcolorbox's
# colored/breakable boxes -- the actual bottleneck). Same \label/\ref
# behavior, ~3x faster. NEVER represents the real book's appearance;
# only use it to check references/errors, never to review layout.
# \include writes aux files named after each chapter, shared with the
# real master -- run `make clean` before switching between the two to
# avoid stale cross-contaminated aux state.
check_fast:
	$(PDFLATEX) --draftmode $(FASTMASTER)

# Fail if the log contains any warning/error other than Overfull/Underfull box warnings.
warnings: pdf
	@if grep -E "Warning|Error" $(MASTER).log | grep -v -E "(Overfull|Underfull) \\\\[hv]box" | grep -q .; then \
		echo "Non-box warnings/errors found in $(MASTER).log:"; \
		grep -E "Warning|Error" $(MASTER).log | grep -v -E "(Overfull|Underfull) \\\\[hv]box"; \
		exit 1; \
	else \
		echo "No warnings/errors other than Overfull/Underfull boxes."; \
	fi

# -n9:  suppress mismatched bracket warning — half-open intervals are correct.
# -n11: suppress "use \cdots" — \dots from amsmath chooses automatically.
# -n17: suppress bracket count mismatch — same reason as -n9.
# -n18: suppress wrong paranthesis wanring
# -n36: suppress "space before (" — f(x) etc. are correct math notation.
# -n38: suppress "punctuation before quotes" — intentional style.

chktex:
	-chktex -f $$'%f:%l:%c: Warning %n: %m\n' -q \
	    -n9 -n11 -n17 -n18 -n36 -n38 \
	    $(MASTER).tex $(wildcard chapters/*.tex)

clean:
	rm -f $(MASTER).aux $(MASTER).bbl $(MASTER).bcf $(MASTER).blg \
	       $(MASTER).log $(MASTER).out $(MASTER).run.xml \
	       $(MASTER).synctex.gz $(MASTER).toc $(MASTER).pdf \
	       $(MASTER).idx $(MASTER).ind $(MASTER).ilg \
	       $(FASTMASTER).aux $(FASTMASTER).bbl $(FASTMASTER).bcf $(FASTMASTER).blg \
	       $(FASTMASTER).log $(FASTMASTER).out $(FASTMASTER).run.xml \
	       $(FASTMASTER).synctex.gz $(FASTMASTER).toc $(FASTMASTER).pdf \
	       $(FASTMASTER).idx $(FASTMASTER).ind $(FASTMASTER).ilg \
	       chapters/*.aux *.aux
