"""Utility functions for burst2stack split workflow."""

import csv
import logging
from datetime import datetime
from pathlib import Path

from burst2safe.utils import BurstInfo

logger = logging.getLogger(__name__)


CSV_FIELDNAMES = [
    'granule',
    'slc_granule',
    'swath',
    'polarization',
    'burst_id',
    'burst_index',
    'direction',
    'absolute_orbit',
    'relative_orbit',
    'date',
    'data_url',
    'data_path',
    'metadata_url',
    'metadata_path',
]


def export_burst_infos_to_csv(burst_infos: list[BurstInfo], csv_path: Path) -> None:
    """Export a list of BurstInfo objects to a CSV file.

    Parameters
    ----------
    burst_infos : list[BurstInfo]
        List of BurstInfo objects to export.
    csv_path : Path
        Path to the output CSV file.
    """
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()

        for info in burst_infos:
            row = {
                'granule': info.granule or '',
                'slc_granule': info.slc_granule or '',
                'swath': info.swath,
                'polarization': info.polarization,
                'burst_id': info.burst_id if info.burst_id is not None else '',
                'burst_index': info.burst_index,
                'direction': info.direction,
                'absolute_orbit': info.absolute_orbit,
                'relative_orbit': info.relative_orbit,
                'date': info.date.isoformat() if info.date else '',
                'data_url': info.data_url or '',
                'data_path': str(info.data_path) if info.data_path else '',
                'metadata_url': info.metadata_url or '',
                'metadata_path': str(info.metadata_path),
            }
            writer.writerow(row)

    logger.info(f'Exported {len(burst_infos)} burst infos to {csv_path}')


def import_burst_infos_from_csv(csv_path: Path) -> list[BurstInfo]:
    """Import a list of BurstInfo objects from a CSV file.

    Parameters
    ----------
    csv_path : Path
        Path to the input CSV file.

    Returns
    -------
    list[BurstInfo]
        List of BurstInfo objects.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    ValueError
        If the CSV file is empty or has invalid format.
    """
    if not csv_path.exists():
        logger.error(f'CSV file not found: {csv_path}')
        raise FileNotFoundError(f'CSV file not found: {csv_path}')

    burst_infos = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            info = BurstInfo(
                granule=row['granule'] if row['granule'] else None,
                slc_granule=row['slc_granule'] if row['slc_granule'] else None,
                swath=row['swath'],
                polarization=row['polarization'],
                burst_id=int(row['burst_id']) if row['burst_id'] else None,
                burst_index=int(row['burst_index']),
                direction=row['direction'],
                absolute_orbit=int(row['absolute_orbit']),
                relative_orbit=int(row['relative_orbit']),
                date=datetime.fromisoformat(row['date']) if row['date'] else None,
                data_url=row['data_url'] if row['data_url'] else None,
                data_path=Path(row['data_path']) if row['data_path'] else None,
                metadata_url=row['metadata_url'] if row['metadata_url'] else None,
                metadata_path=Path(row['metadata_path']),
            )
            burst_infos.append(info)

    if not burst_infos:
        logger.error(f'No burst infos found in CSV file: {csv_path}')
        raise ValueError(f'No burst infos found in CSV file: {csv_path}')

    logger.info(f'Imported {len(burst_infos)} burst infos from {csv_path}')
    return burst_infos
