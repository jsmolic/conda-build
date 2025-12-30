# Copyright (C) 2014 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import logging
import os
import pkgutil
import subprocess
import sys
from importlib import import_module
from typing import TYPE_CHECKING
from pathlib import Path

from conda.base.context import context

from .. import api
from ..config import Config

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace
    from collections.abc import Sequence

from rattler_build._rattler_build import (
    generate_cpan_recipe_string_py,
    generate_luarocks_recipe_string_py,
    generate_pypi_recipe_string_py,
    generate_r_recipe_string_py,
)

thisdir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO)

def generate_recipe_rattler_build(
    package: str | Iterable[str],
    repo: Literal["cpan", "cran", "luarocks", "pypi", "rpm"],
    version: str | None = None,
) -> str:
    """Generate rattler-build recipe YAML string for the specified repository."""
    
    package = package[0]

    match repo:
        case "cpan":
            recipe_yaml = generate_cpan_recipe_string_py(package)
        case "cran":
            recipe_yaml = generate_r_recipe_string_py(package)
        case "luarocks":
            recipe_yaml = generate_luarocks_recipe_string_py(package)
        case "pypi":
            recipe_yaml = generate_pypi_recipe_string_py(package)

    return recipe_yaml

def parse_args(args: Sequence[str] | None) -> tuple[ArgumentParser, Namespace]:
    from conda.cli.conda_argparse import ArgumentParser

    parser = ArgumentParser(
        prog="conda skeleton",
        description="""
Generates a boilerplate/skeleton recipe, which you can then edit to create a
full recipe. Some simple skeleton recipes may not even need edits.
        """,
        epilog="""
Run --help on the subcommands like 'conda skeleton pypi --help' to see the
options available.
        """,
    )

    # Flag for using rattler-build
    parser.add_argument(
        "--use-rattler",
        action="store_true",
        help="Generate recipes using rattler-build",
    )

    repos = parser.add_subparsers(dest="repo")

    skeletons = [
        name
        for _, name, _ in pkgutil.iter_modules([os.path.join(thisdir, "../skeletons")])
    ]
    for skeleton in skeletons:
        if skeleton.startswith("_"):
            continue
        module = import_module("conda_build.skeletons." + skeleton)
        module.add_parser(repos)

    return parser, parser.parse_args(args)


def execute(args: Sequence[str] | None = None) -> int:
    parser, parsed = parse_args(args)
    context.__init__(argparse_args=parsed)

    config = Config(**parsed.__dict__)

    if not parsed.repo:
        parser.print_help()
        sys.exit()

    if parsed.use_rattler:
        if parsed.repo == "rpm":
            print(
                f"Warning: rattler-build does not support '{parsed.repo}' skeleton"
                "Falling back to conda-skeleton recipe generation.",
                file=sys.stderr,
            )
        else:
            recipe_yaml = generate_recipe_rattler_build(
                parsed.packages,
                parsed.repo,
                parsed.version
            )

            if isinstance(parsed.packages, str):
                packages = [parsed.packages]
            else:
                packages = list(parsed.packages)
            
            for package in parsed.packages:
                output_dir = Path(parsed.output_dir or ".")
                output_dir.mkdir(parents=True, exist_ok=True)
                package_dir = output_dir / package
                package_dir.mkdir(parents=True, exist_ok=True)
                recipe_path = package_dir / "recipe.yaml"
                recipe_path.write_text(recipe_yaml)
                print(f"Recipe written to: {recipe_path}")

            return 0


            #output_dir = Path(parsed.output_dir or ".")
            #output_dir.mkdir(parents=True, exist_ok=True)

            #recipe_path = output_dir / f"{package.replace('/', '-')}_recipe.yaml"
            #recipe_path.write_text(recipe_yaml)
            #print(f"Recipe written to: {recipe_path}")

            # cmd = [
            #     "rattler-build",
            #     "generate-recipe",
            #     parsed.repo,
            #     *parsed.packages,
            #     "-w",
            # ]
            # try:
            #     subprocess.run(cmd, text=True, check=True)
            #     return 0
            # except subprocess.CalledProcessError as e:
            #     print(f"rattler-build failed: {e}", file=sys.stderr)
            #     return e.returncode

    api.skeletonize(
        parsed.packages,
        parsed.repo,
        output_dir=parsed.output_dir,
        recursive=parsed.recursive,
        version=parsed.version,
        config=config,
    )

    return 0
