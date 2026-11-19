# TDM-GEO-maz_numbering

Assigns a new, consecutive `MAZID` (1 to N) to every microzone (MAZ) in the Wasatch Front travel demand model, using geopandas.

Geometry cleaning (gaps, slivers, TAZ crossovers) is done upstream in `Microzones Geometry Cleanup.ipynb`, which is kept here as a read-only reference. This repo only does the numbering.

## Numbering rules

1. Each MAZ is located by its **representative point** (always inside the polygon).
2. `TAZID` is assigned with a **point-in-polygon** join of that point to the TAZ layer.
3. MAZs are numbered **TAZ by TAZ**, in ascending `TAZID`.
4. Within a TAZ the order is **north to south, then west to east** (strict sort on the point's Y descending, then X ascending).
5. `MAZID` is one sequence for the whole region, starting at 1 with no gaps.
6. The previous ID is kept in `MAZID_OLD` until the result is approved.

All analysis is in **EPSG:26912**.

## Run it

Requires [uv](https://docs.astral.sh/uv/) and [Quarto](https://quarto.org/).

```powershell
uv sync
uv run quarto render index.qmd --no-execute-daemon
```

The render writes:

| File | What |
| --- | --- |
| `index.html` | The analysis report (not committed) |
| `data/output/maz_numbered.shp` | MAZ with new `MAZID`, `MAZID_OLD`, `TAZID` |
| `data/output/maz_qc_map.html` | Interactive folium QC map, colored by `MAZID` (not committed) |

The report ends with QC checks (1..N, no gaps or duplicates, one TAZ per MAZ, TAZ order, north-to-south order). The render fails if any check fails.

## Data

All inputs are cached in the repo as shapefiles in `data/raw/`, so the analysis never reads the network or the `D:` drive. A cache file is only created if it is missing.

| Dataset | Cache | Source |
| --- | --- | --- |
| TAZ | `data/raw/taz.shp` | [WasatchFrontTAZ feature service](https://services1.arcgis.com/taguadKoI1XFwivx/ArcGIS/rest/services/WasatchFrontTAZ/FeatureServer/0), downloaded by `src/get_data.py` |
| MAZ | `data/raw/maz_source.shp` | Layer `_18_maz_spatially_sorted` in `Microzones_Cleaner.gdb`, exported by `scripts/export_maz_arcpy.py` |

Download dates are recorded in `data/raw/CACHE_INFO.json`.

**Refresh TAZ:** delete `data/raw/taz.*` and rerun the render (or `uv run python -m src.get_data`).

**Refresh MAZ:** delete `data/raw/maz_source.*`, then run the export with ArcGIS Pro's Python. geopandas cannot read this layer from the geodatabase, but arcpy can:

```powershell
& "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" scripts/export_maz_arcpy.py
```

## Layout

```
index.qmd                  analysis (exploratory, step by step)
_quarto.yml                project and render settings (python3 kernel)
src/config.py              paths and constants
src/get_data.py            only-if-missing TAZ download and cache loading
scripts/export_maz_arcpy.py  one-time MAZ export (needs ArcGIS Pro)
data/raw/                  cached inputs (shapefile)
data/output/               results (shapefile)
AGENTS.md                  instructions for AI coding agents
```

## Notes

- Shapefile field names are limited to 10 characters.
- `MAZID_OLD` is temporary and will be dropped once the numbering is approved.
- Run Quarto with `--no-execute-daemon`. A running kernel can keep stale versions of the `src` modules.
