# Compile Notes

LaTeX compilation was not run during release packaging because neither
`latexmk` nor `pdflatex` was available on PATH in the packaging environment.

Expected local compile command:

```bash
cd docs/manuscript
latexmk -pdf main.tex
```

Fallback:

```bash
pdflatex main.tex
```

The manuscript intentionally includes `TODO_CITATION` placeholders where
references still need to be verified before workshop or preprint submission.
