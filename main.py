#!/usr/bin/env python3.9
import asyncio

import server
from data.cli_arguments import cli_arguments
from data.config import FORTIFY_APP_NAME
from fortify.scan import run_scan
from tools.analyse_setup import check_sources
from sys import exit

if __name__ == '__main__':
    source_path = cli_arguments.sources
    if source_path.is_dir():
        source_path = source_path.joinpath(FORTIFY_APP_NAME)
    print(f'Try to use {source_path}')
    if not check_sources(source_path=source_path):
        print("Sources not found or have some error, check fortify")
        exit(0)
    print(f"Sources found in {source_path}")
    if cli_arguments.local:
        run_scan(target=cli_arguments.target,
                 output=cli_arguments.output,
                 output_format=cli_arguments.output_format,
                 sources=source_path)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(server.socket_listener())
