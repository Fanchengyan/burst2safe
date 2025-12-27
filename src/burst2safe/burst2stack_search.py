"""A tool for searching ASF burst SLCs and exporting to CSV."""

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from shapely.geometry import Polygon

from burst2safe import utils
from burst2safe.burst2stack_utils import export_burst_infos_to_csv
from burst2safe.safe import Safe
from burst2safe.search import find_group


DESCRIPTION = """Search ASF burst SLCs and export burst information to CSV.
This is the first step in the burst2stack workflow. Use the output CSV
with burst2stack-download and burst2stack-merge commands.
"""


def burst2stack_search(
    extent: Polygon,
    rel_orbit: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    polarizations: list[str] | None = None,
    swaths: list[str] | None = None,
    mode: str = 'IW',
    min_bursts: int = 1,
    output_csv: Path | None = None,
    work_dir: Path | None = None,
) -> Path:
    """Search ASF burst SLCs and export to CSV file.

    Parameters
    ----------
    extent : Polygon
        The bounding box of the bursts.
    rel_orbit : int | None, optional
        The relative orbit number of the bursts.
    start_date : datetime | None, optional
        The start date of the bursts.
    end_date : datetime | None, optional
        The end date of the bursts.
    polarizations : list[str] | None, optional
        List of polarizations to include.
    swaths : list[str] | None, optional
        List of swaths to include.
    mode : str, optional
        The collection mode to use (IW or EW). Default is 'IW'.
    min_bursts : int, optional
        The minimum number of bursts per swath. Default is 1.
    output_csv : Path | None, optional
        Path to output CSV file. Default is 'bursts.csv' in work_dir.
    work_dir : Path | None, optional
        The directory to save data files. Default is current directory.

    Returns
    -------
    Path
        Path to the output CSV file.
    """
    work_dir = utils.optional_wd(work_dir)

    # Search for bursts
    print('Searching for bursts...')
    burst_search_results = find_group(
        rel_orbit,
        extent,
        polarizations,
        swaths,
        mode,
        min_bursts,
        use_relative_orbit=True,
        start_date=start_date,
        end_date=end_date,
    )
    burst_infos = utils.get_burst_infos(burst_search_results, work_dir)
    abs_orbits = utils.drop_duplicates([burst_info.absolute_orbit for burst_info in burst_infos])
    print(f'Found {len(burst_infos)} burst(s), comprising {len(abs_orbits)} SAFE(s).')

    # Validate burst groups before export
    print('Checking burst group validities...')
    burst_sets = [[bi for bi in burst_infos if bi.absolute_orbit == orbit] for orbit in abs_orbits]
    for burst_set in burst_sets:
        Safe.check_group_validity(burst_set)
    print('All burst groups are valid.')

    # Export to CSV
    if output_csv is None:
        output_csv = work_dir / 'bursts.csv'
    else:
        output_csv = Path(output_csv)

    export_burst_infos_to_csv(burst_infos, output_csv)
    print(f'Exported {len(burst_infos)} burst(s) to {output_csv}')

    return output_csv


def main() -> None:
    """Command-line entry point for burst2stack-search."""
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--rel-orbit', type=int, help='Relative orbit number of the bursts')
    parser.add_argument('--start-date', type=str, help='Start date of the bursts (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date of the bursts (YYYY-MM-DD)')
    parser.add_argument(
        '--extent',
        type=str,
        nargs='+',
        help='Bounds (W S E N in lat/lon) or geometry file describing spatial extent',
        required=True,
    )
    parser.add_argument('--pols', type=str, nargs='+', help='Polarizations of the bursts (i.e., VV VH)')
    parser.add_argument('--swaths', type=str, nargs='+', help='Swaths of the bursts (i.e., IW1 IW2 IW3)')
    parser.add_argument('--mode', type=str, default='IW', help='Collection mode to use (IW or EW). Default: IW')
    parser.add_argument('--min-bursts', type=int, default=1, help='Minimum # of bursts per swath/polarization.')
    parser.add_argument('--output-csv', type=str, default=None, help='Output CSV file path. Default: bursts.csv')
    parser.add_argument('--output-dir', type=str, default=None, help='Output directory to save to')

    args = utils.reparse_args(parser.parse_args(), tool='burst2stack')

    burst2stack_search(
        rel_orbit=args.rel_orbit,
        start_date=args.start_date,
        end_date=args.end_date,
        extent=args.extent,
        polarizations=args.pols,
        swaths=args.swaths,
        mode=args.mode,
        min_bursts=args.min_bursts,
        output_csv=Path(args.output_csv) if args.output_csv else None,
        work_dir=Path(args.output_dir) if args.output_dir else None,
    )


if __name__ == '__main__':
    main()
