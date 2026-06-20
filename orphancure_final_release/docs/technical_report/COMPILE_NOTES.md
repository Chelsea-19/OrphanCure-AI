# Compile Notes

LaTeX compilation was not run during release packaging because neither
`latexmk` nor `pdflatex` was available on PATH in the packaging environment.

Expected local compile command:

```bash
cd docs/technical_report
latexmk -pdf main.tex
```

Fallback:

```bash
pdflatex main.tex
```

The source is written to compile with standard LaTeX packages:
`graphicx`, `booktabs`, `longtable`, `hyperref`, `array`, and `xcolor`.
