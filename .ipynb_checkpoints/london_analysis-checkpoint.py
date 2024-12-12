import polars as pl

from pathlib import Path


def load_london_places() -> pl.DataFrame:
    """Filter UK places to the rough coordinate box of London"""
    # Start with dataset filtered to just the `country = "UK"` subset
    return pl.read_parquet("fsq-osp_uk.zstd.parquet").filter(
        pl.col("latitude").is_between(51.42, 51.59), # Streatham, Tottenham (South, North)
        pl.col("longitude").is_between(-0.24, 0.02), # Putney, Greenwich (West, East)
    )

def load_places_geojson(places: pl.DataFrame) -> str:
    return {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [coord["longitude"], coord["latitude"]],
                },
                'properties': coord,
            }
            for coord in places.to_dicts()
        ],
    }