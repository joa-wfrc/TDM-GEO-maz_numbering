"""Central configuration. All paths are relative to the repo root."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "output"

CRS = "EPSG:26912"

# Local caches (Shapefile). Downloaded only if missing, see get_data.py.
TAZ_SHP = RAW / "taz.shp"
MAZ_SHP = RAW / "maz_source.shp"
CACHE_INFO = RAW / "CACHE_INFO.json"

TAZ_URL = (
    "https://services1.arcgis.com/taguadKoI1XFwivx/ArcGIS/rest/services/"
    "WasatchFrontTAZ/FeatureServer/0"
)
MAZ_GDB = r"D:\ABM-INP-Microzones\Scripts\Scratch\Microzones_Cleaner\Microzones_Cleaner.gdb"
MAZ_LAYER = "_18_maz_spatially_sorted"

OUT_SHP = OUT / "maz_numbered.shp"
QC_MAP = OUT / "maz_qc_map.html"
