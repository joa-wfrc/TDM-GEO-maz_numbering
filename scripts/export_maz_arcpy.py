"""One-time export of the MAZ layer from the file geodatabase to the repo cache.

GDAL (geopandas) cannot see this layer in the geodatabase, but arcpy can. Run this with
ArcGIS Pro's Python, from the repo root, only when data/raw/maz_source.shp is missing:

    "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" scripts/export_maz_arcpy.py
"""
import json
import sys
from datetime import date
from pathlib import Path

import arcpy

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import config  # noqa: E402

if config.MAZ_SHP.exists():
    print(f"{config.MAZ_SHP.name} already exists. Delete it to re-export.")
    sys.exit(0)

config.RAW.mkdir(parents=True, exist_ok=True)
src = f"{config.MAZ_GDB}\{config.MAZ_LAYER}"
arcpy.management.CopyFeatures(src, str(config.MAZ_SHP))
print("Exported", arcpy.management.GetCount(str(config.MAZ_SHP))[0], "features")

info = json.loads(config.CACHE_INFO.read_text()) if config.CACHE_INFO.exists() else {}
info["maz"] = {"source": src, "downloaded": date.today().isoformat()}
config.CACHE_INFO.write_text(json.dumps(info, indent=2))
