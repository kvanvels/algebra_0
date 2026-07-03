XELATEX = xelatex -file-line-error -interaction=nonstopmode
MASTER  = master

.PHONY: pdf quick check clean chktex warnings

pdf: $(MASTER).pdf

$(MASTER).pdf: $(MASTER).tex $(wildcard *.tex) $(wildcard chapters/*.tex)
	$(XELATEX) $(MASTER)
	biber $(MASTER)
	$(XELATEX) $(MASTER)
	$(XELATEX) $(MASTER)

quick:
	$(XELATEX) $(MASTER)

check:
	$(XELATEX) -no-pdf $(MASTER)

# Fail if the log contains any warning other than Overfull/Underfull box warnings.
warnings: pdf
	@if grep -E "Warning" $(MASTER).log | grep -v -E "(Overfull|Underfull) \\\\[hv]box" | grep -q .; then \
		echo "Non-box warnings found in $(MASTER).log:"; \
		grep -E "Warning" $(MASTER).log | grep -v -E "(Overfull|Underfull) \\\\[hv]box"; \
		exit 1; \
	else \
		echo "No warnings other than Overfull/Underfull boxes."; \
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
