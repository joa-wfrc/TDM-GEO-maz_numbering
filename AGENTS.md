# AGENTS.md

Guidance for AI coding agents working in this repository (`TDM-GEO-maz_numbering`).

## 1. Objective

Assign a new, unique `MAZID` to every microzone (MAZ) polygon in the already-cleaned MAZ layer.

Rules:

1. Use each polygon's **representative point** (`GeoSeries.representative_point()`, which is guaranteed to fall inside the polygon) for all assignment and ordering.
2. Assign `TAZID` to each MAZ with a **point-in-polygon** spatial join: the representative point against the TAZ polygons.
3. Number **TAZ by TAZ**, in ascending `TAZID` order. All MAZs in the first TAZ are numbered before any in the next.
4. Within each TAZ, order MAZs **north to south first, then west to east**. Use a **strict sort**: representative point Y descending, then X ascending. No banding or tolerance.
5. `MAZID` is **one consecutive sequence for the whole region**: it starts at 1, has no gaps, and ends at the total MAZ count.
6. Move the existing `MAZID` to `MAZID_OLD` and write the new numbers to `MAZID`. `MAZID_OLD` will be deleted later, once the result is approved.

## 2. Scope

- **In scope:** MAZ numbering only, written in Quarto markdown (`.qmd`) with Python and geopandas.
- **Out of scope:** geometry cleaning (gap filling, slivers, TAZ crossovers). That is done in `Microzones Geometry Cleanup.ipynb`. The input MAZ layer (`_18_maz_spatially_sorted`) is assumed to be already cleaned. Do not reimplement cleaning in the `.qmd`.
- `Microzones Geometry Cleanup.ipynb` is a **read-only reference** (an earlier arcpy attempt). **Do not edit it.** It will later be moved to `_archive/`. Leave it where it is for now.

## 3. Tech Stack and Tooling

| Item | Requirement |
| --- | --- |
| Version control | Git (initialize if needed) |
| Python management | `uv` |
| Python version | 3.14 |
| Spatial analysis | `geopandas` only (no arcpy) |
| Analysis document | Quarto markdown (`.qmd`) |
| CRS | **EPSG:26912**. Reproject all inputs to it before any spatial operation. |
| Mapping | `folium` (interactive QC map) |
| Remote | Private repo in the user's **personal** GitHub account (standard GitHub, no Git LFS), published as **`TDM-GEO-maz_numbering`**. The local folder name stays as it is. |

## 4. Data Sources

| Dataset | Location | Notes |
| --- | --- | --- |
| TAZ | https://services1.arcgis.com/taguadKoI1XFwivx/ArcGIS/rest/services/WasatchFrontTAZ/FeatureServer/0 | ArcGIS REST feature service. Download once and save in the repo. |
| MAZ | `D:\ABM-INP-Microzones\Scripts\Scratch\Microzones_Cleaner\Microzones_Cleaner.gdb`, layer `_18_maz_spatially_sorted` | Local file geodatabase. geopandas reads it directly. |

## 5. Data Rules

- **All data used by the analysis must live inside this repo** so it is reproducible. The `.qmd` must not read from `D:\` or from the web.
- **Local cache for TAZ:** the analysis works only from the local TAZ copy in the repo.
- Provide a download script (for example `scripts/get_data.py`) that fetches the TAZ service and saves it to the local cache. The script **downloads only if the cached file is missing**. To refresh the data, the user deletes the cached file and reruns the script. The `.qmd` calls the script (or the download function) so the step is reproducible.
- The MAZ geodatabase layer is also copied once into the repo by the script, using the same only-if-missing rule.
- Record the download date alongside the cache (for example in a small metadata or README file).
- Store local data and outputs as **Shapefile (`.shp`)**.
- The final output is a MAZ shapefile with `MAZID` (new) and `MAZID_OLD` (previous).
- Shapefile limits: field names are limited to 10 characters, so use short names. Keep `MAZID` and `MAZID_OLD`.

## 6. Analysis Style

`index.qmd` is the single analysis document. Write it as an **exploratory data science notebook**, not as a program:

- Prefer top-level, step-by-step code over helper functions. Define a function only when the same logic is used three or more times.
- Inspect before transforming: look at shapes, dtypes, nulls, uniques, CRS and geometry validity.
- Check each step's result (row counts before and after joins, unmatched rows, duplicates) before moving on.
- Plot as you go (matplotlib for quick checks) and finish with the folium QC map.
- Put short plain-language prose between code chunks explaining what and why.
- Put the cache and download logic in `src/get_data.py`, and keep paths and constants in `src/config.py`.
- Use `assert` for QC at the end, and make failures obvious.

## 7. Conventions

- Run Python through `uv` (`uv run ...`, `uv add ...`). Do not call `pip` directly.
- Use paths relative to the repo root. No hard-coded absolute paths in analysis code.
- Do not commit or push unless asked.
- Add QC checks to the `.qmd`: no null `MAZID`, no duplicates, IDs are exactly 1..N, every MAZ has exactly one `TAZID`, and the feature count matches the input.

## 8. QC Map

As part of QC, the `.qmd` must include an interactive **folium** map of the new `MAZID` for visual verification:

- Color the MAZ polygons by `MAZID` using a sequential color ramp, so the numbering order is visible across each TAZ and the region.
- Include a legend or colorbar, a tooltip showing `MAZID`, `MAZID_OLD` and `TAZID`, and a TAZ boundary overlay.
- Reproject to EPSG:4326 for folium only. All analysis stays in EPSG:26912.
