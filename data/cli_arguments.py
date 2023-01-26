import argparse
from pathlib import Path

from data.config import FORTIFY_APP, PARENT_BASE, DEFAULT_OUTPUT_FORMAT, DEFAULT_OUTPUT_FILE


def create_parser():
    parser = argparse.ArgumentParser(description='Fortify Server')
    parser.add_argument('-ht', '--host', type=str, default='0.0.0.0',
                        help='Server host. Default 0.0.0.0')
    parser.add_argument('-p', '--port', type=int, default=33333,
                        help='Server port. Default 33333')
    parser.add_argument('-s', '--sources', type=Path, default=FORTIFY_APP,
                        help=f'Path to fortify scan application. Default is {FORTIFY_APP}')
    parser.add_argument('-l', '--local', default=False, action='store_true',
                        help='[Only for local scan] Use if want to analyze target locally')
    parser.add_argument('-o', '--output', type=Path, default=DEFAULT_OUTPUT_FILE,
                        help='Output file')
    parser.add_argument('-of', '--output-format', default=DEFAULT_OUTPUT_FORMAT,
                        help=f'[Only for local scan] File extension for output. Default: {DEFAULT_OUTPUT_FORMAT}')
    parser.add_argument('-t', '--target', type=Path, default=PARENT_BASE,
                        help=f'[Only for local scan] Path for analyzing. Default {PARENT_BASE}')
    parser.add_argument('-dt', '--delete-time', type=int, default=7,
                        help='Days that other generated project will be kept. Default 7')
    return parser.parse_args()


cli_arguments = create_parser()
