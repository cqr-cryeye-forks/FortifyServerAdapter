from pathlib import Path

from data.cli_arguments import cli_arguments
from fortify.fortify_base import FortifyScan


def run_scan(target: Path,
             output: Path = None,
             output_format: str = cli_arguments.output_format,
             sources: Path = cli_arguments.sources,
             clean_results: bool = False):
    fortify_obj = FortifyScan(target=target,
                              output=output, output_format=output_format,
                              sources=sources, clean_results=clean_results)
    return fortify_obj.run_scan()
