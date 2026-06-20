# repoDB Data Placement

Place the final repoDB CSV here as:

```text
data/benchmarks/repodb/repodb.csv
```

Source:

- Brown AS, Patel CJ. A standard database for drug repositioning.
  Scientific Data 4:170029 (2017). doi:10.1038/sdata.2017.29
- Figshare collection DOI: `10.6084/m9.figshare.c.3462048`

The real benchmark CSV is not committed by default. Use:

```bash
python scripts/evaluate_repodb.py --download-only
```

or download it manually from Figshare and place it at the path above.

