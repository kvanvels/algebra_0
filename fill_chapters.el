;;; fill_chapters.el --- batch worker for fill_chapters.sh  -*- lexical-binding: t; -*-

;; Not meant to be run directly; see fill_chapters.sh.
;;
;; Visits each file named on the command line, runs AUCTeX's
;; `LaTeX-fill-buffer' (the same thing `C-c C-q C-p'/`M-q' does for a single
;; paragraph, but for the whole buffer), and saves.
;;
;; `--batch' skips the normal package-initialize that a real session does,
;; so AUCTeX (installed via package.el under ~/.emacs.d/elpa) isn't on
;; load-path unless we do it ourselves here.

(require 'package)
(package-initialize)
(require 'latex)

(dolist (file command-line-args-left)
  (find-file file)
  (LaTeX-mode)
  (LaTeX-fill-buffer nil)
  (save-buffer)
  (kill-buffer))

(setq command-line-args-left nil)

;;; fill_chapters.el ends here
