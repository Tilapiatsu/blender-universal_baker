from __future__ import annotations

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
    def resolve(cls, context: OutputContext) -> OutputFile:

        directory = cls.resolve_directory(context.directory_template, context)
        filename = cls.resolve_filename(context.filename_template, context)

        path = directory / f"{filename}.{context.extension}"

        return OutputFile(
            directory=directory,
            filename=filename,
            extension=context.extension,
            absolute_path=path,
            settings=context.output_settings,
        )

    # -------------------------------------------------------------------------
    # Directory
    # -------------------------------------------------------------------------

    @classmethod
    def resolve_directory(cls, template: str, context: OutputContext) -> Path:
        return Path(cls.expand(template, context))

    # -------------------------------------------------------------------------
    # Filename
    # -------------------------------------------------------------------------

    @classmethod
    def resolve_filename(cls, template: str, context: OutputContext) -> str:
        return cls.expand(template, context)

    # -------------------------------------------------------------------------
    # Template expansion
    # -------------------------------------------------------------------------

    @classmethod
    def expand(cls, template: str, context: OutputContext) -> str:
        return _TOKEN_PATTERN.sub(
            lambda match: cls._resolve_token(
                match.group(1),
                context,
            ),
            template,
        )

    # -------------------------------------------------------------------------
    # Token resolution
    # -------------------------------------------------------------------------

    @classmethod
    def _resolve_token(cls, token: str, context: OutputContext) -> str:
        parts = token.split(".")

        name = parts[0]

        transforms = parts[1:]

        value = registry_token.resolve(name, context)

        for transform in transforms:
            value = registry_transform.apply(value, transform)

        return value
