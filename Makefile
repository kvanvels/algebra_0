LUALATEX = lualatex -file-line-error -interaction=nonstopmode
MASTER   = master

.PHONY: pdf quick check_syntax clean chktex warnings

pdf: $(MASTER).pdf

$(MASTER).pdf: $(MASTER).tex $(wildcard *.tex) $(wildcard chapters/*.tex)
	$(LUALATEX) $(MASTER)
	biber $(MASTER)
	$(LUALATEX) $(MASTER)
	$(LUALATEX) $(MASTER)

quick:
	$(LUALATEX) $(MASTER)

# Fast pass with no PDF output, for catching errors/undefined refs
# without paying for font loading and page output.
check_syntax:
	$(LUALATEX) --draftmode $(MASTER)

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
# -n36: suppress "space before (" — f(x) etc. are correct math notation.
# -n38: suppress "punctuation before quotes" — intentional style.
chktex:
	-chktex -f $$'%f:%l:%c: Warning %n: %m\n' -q \
	    -n9 -n11 -n17 -n36 -n38 \
	    $(MASTER).tex $(wildcard chapters/*.tex)

clean:
	rm -f $(MASTER).aux $(MASTER).bbl $(MASTER).bcf $(MASTER).blg \
	       $(MASTER).log $(MASTER).out $(MASTER).run.xml \
	       $(MASTER).synctex.gz $(MASTER).toc $(MASTER).pdf \
	       chapters/*.aux *.aux
