from __future__ import annotations

import bpy

import re

from pathlib import Path

from typing import Callable

from ..runtime.output_context import OutputContext
from ..runtime.output_file import OutputFile
from ..core.registry_token import registry_token
from ..core.registry_transform import registry_transform


_TOKEN_PATTERN = re.compile(r"\{([^{}]+)\}")


class OutputResolver:
    """
    Resolves filename and directory templates into concrete output paths.
    """

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @classmethod
    def resolve(cls, ctx: OutputContext) -> OutputFile:
        relative = ""
        if ctx.directory_template.startswith(r"//"):
            ctx.directory_template = ctx.directory_template[2:]
            relative = r"//"

        directory = cls.resolve_directory(ctx.directory_template, ctx)
        filename = cls.resolve_filename(ctx.filename_template, ctx)

        path = Path.as_posix(relative / directory / f"{filename}.{ctx.extension.lower()}")

        return OutputFile(
            directory=directory,
            filename=filename,
            extension=ctx.extension,
            absolute_path=Path(bpy.path.abspath(str(path))),
            settings=ctx.output_settings,
        )

    # -------------------------------------------------------------------------
    # Directory
    # -------------------------------------------------------------------------

    @classmethod
    def resolve_directory(cls, template: str, ctx: OutputContext) -> Path:
        return Path(cls.expand(template, ctx))

    # -------------------------------------------------------------------------
    # Filename
    # -------------------------------------------------------------------------

    @classmethod
    def resolve_filename(cls, template: str, ctx: OutputContext) -> str:
        return cls.expand(template, ctx)

    # -------------------------------------------------------------------------
    # Template expansion
    # -------------------------------------------------------------------------

    @classmethod
    def expand(cls, template: str, ctx: OutputContext) -> str:
        return _TOKEN_PATTERN.sub(
            lambda match: cls._resolve_token(
                match.group(1),
                ctx,
            ),
            template,
        )

    # -------------------------------------------------------------------------
    # Token resolution
    # -------------------------------------------------------------------------

    @classmethod
    def _resolve_token(cls, token: str, ctx: OutputContext) -> str:
        parts = token.split(".")

        name = parts[0]

        transforms = parts[1:]

        value = registry_token.resolve(name, ctx)

        for transform in transforms:
            value = registry_transform.apply(value, transform)

        return value
