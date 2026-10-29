from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any

import bpy

from ..core.registry_token import registry_token
from ..core.registry_transform import registry_transform
from ..enum.image_layout import ImageLayout
from ..runtime.output_context import OutputContext
from ..runtime.output_file import OutputFile

_TOKEN_PATTERN = re.compile(r"\{([^{}]+)\}")


class OutputResolver:
    """
    Resolves filename and directory templates into concrete output paths.
    """

    @classmethod
    def resolve(
        cls,
        ctx: OutputContext,
        image_layout: ImageLayout,
        suffix: str | None = None,
        sub_folder: str | None = None,
    ) -> OutputFile:
        relative = ""
        dir = ctx.directory_template
        if dir.startswith(r"//"):
            dir = dir[2:]
            relative = r"//"

        directory = cls.resolve_directory(dir, ctx.variables)
        filename = cls.resolve_filename(ctx.filename_template, ctx.variables)

        if suffix is not None:
            filename += f"_{suffix}"

        if image_layout == ImageLayout.UDIM:
            filename += ".<UDIM>"

        if sub_folder is not None:
            directory = directory / sub_folder

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
    def resolve_directory(
        cls, template: str, variables: dict[str, Any] | None = None, resolve_relative: bool = False
    ) -> Path:
        variables = {} if variables is None else variables
        p = Path(cls.expand(template, variables))

        if resolve_relative:
            relative_to = cls.blend_file_path()
            if str(relative_to) == ".":
                relative_to = cls.tempdir()
            p = cls.resolve_relative(p, relative_to)

        return p

    @classmethod
    def resolve_relative(cls, path: Path, relative_to: Path) -> Path:
        result = path

        if str(path).startswith("//"):
            result = Path(str(path).replace("//", str(relative_to) + "/"))

        return result

    @staticmethod
    def blend_file_path() -> Path:
        return Path(bpy.path.abspath("//"))

    @staticmethod
    def tempdir() -> Path:
        return Path(tempfile.gettempdir())

    # -------------------------------------------------------------------------
    # Filename
    # -------------------------------------------------------------------------

    @classmethod
    def resolve_filename(cls, template: str, variables: dict[str, Any] | None = None) -> str:
        variables = {} if variables is None else variables
        return cls.expand(template, variables)

    # -------------------------------------------------------------------------
    # Template expansion
    # -------------------------------------------------------------------------

    @classmethod
    def expand(cls, template: str, variables: dict[str, Any]) -> str:
        return _TOKEN_PATTERN.sub(
            lambda match: cls._resolve_token(
                match.group(1),
                variables,
            ),
            template,
        )

    # -------------------------------------------------------------------------
    # Token resolution
    # -------------------------------------------------------------------------

    @classmethod
    def _resolve_token(cls, token: str, variables: dict[str, Any]) -> str:
        parts = token.split(".")

        name = parts[0]
        transforms = parts[1:]
        value = registry_token.resolve(name, variables)

        for transform in transforms:
            value = registry_transform.apply(value, transform)

        return value
