"""Create the local data caches. Each step runs only if its cache file is missing.

To refresh a dataset: delete its .shp (and sidecar files) in data/raw/ and rerun
    uv run python -m src.get_data
"""
import json
from datetime import date

import geopandas as gpd
import pandas as pd
import requests

from src import config


def _record(key: str, source: str) -> None:
    info = json.loads(config.CACHE_INFO.read_text()) if config.CACHE_INFO.exists() else {}
    info[key] = {"source": source, "downloaded": date.today().isoformat()}
    config.CACHE_INFO.write_text(json.dumps(info, indent=2))


def _fetch_arcgis_layer(url: str) -> gpd.GeoDataFrame:
    """Download a whole ArcGIS FeatureServer layer, paging past maxRecordCount."""
    query = f"{url}/query"
    frames, offset = [], 0
    while True:
        params = {
            "where": "1=1", "outFields": "*", "f": "geojson",
            "outSR": config.CRS.split(":")[1],
            "resultOffset": offset, "resultRecordCount": 1000,
            "orderByFields": "FID",
        }
        resp = requests.get(query, params=params, timeout=120)
        resp.raise_for_status()
        if "error" in resp.json():
            raise RuntimeError(resp.json()["error"])
        gdf = gpd.GeoDataFrame.from_features(resp.json()["features"], crs=config.CRS)
        if gdf.empty:
            break
        frames.append(gdf)
        offset += len(gdf)
    if not frames:
        raise RuntimeError(f"No features returned from {url}")
    return gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=config.CRS)


def ensure_taz() -> gpd.GeoDataFrame:
    if not config.TAZ_SHP.exists():
        print("TAZ cache missing: downloading...")
        config.RAW.mkdir(parents=True, exist_ok=True)
        taz = _fetch_arcgis_layer(config.TAZ_URL).to_crs(config.CRS)
        taz["TAZID"] = taz["TAZID"].astype(int)
        taz.to_file(config.TAZ_SHP)
        _record("taz", config.TAZ_URL)
    return gpd.read_file(config.TAZ_SHP).to_crs(config.CRS)


def ensure_maz() -> gpd.GeoDataFrame:
    if not config.MAZ_SHP.exists():
        raise FileNotFoundError(
            f"{config.MAZ_SHP} is missing. Run scripts/export_maz_arcpy.py with ArcGIS Pro Python "
            "(geopandas cannot read this layer from the geodatabase)."
        )
    return gpd.read_file(config.MAZ_SHP).to_crs(config.CRS)


if __name__ == "__main__":
    taz, maz = ensure_taz(), ensure_maz()
    print(f"TAZ: {len(taz):,} features | MAZ: {len(maz):,} features")
