from __future__ import annotations

from pathlib import Path

import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, PointerProperty, StringProperty
from bpy.types import PropertyGroup

from ..constant import LOG, NAME_DICT_BAKER
from ..parameters_definition.baker_settings import UBK_BakerSettings
from .custom_baker import UBK_CustomBaker
from .settings_bake import UBK_BakeSettings

updating = False


def update_image_name(self, context):
    from ..core.controller import BakeController
    from ..output.output_tokens import get_variables

    global updating

    if not updating:
        updating = True
        NAME_DICT_BAKER.pop(self.uuid, None)
        self.image_name = BakeController.get_unique_name(self.image_name, self.uuid, NAME_DICT_BAKER)
        updating = False
    else:
        return

    project = BakeController.project(context)

    if project is None:
        return

    bake_group = BakeController.active_bake_group(context)

    if bake_group is None:
        return

    template = (
        self.settings.output_settings.filename_template
        if self.override_settings
        else project.settings_bake.output_settings.filename_template
    )

    from ..core.output_resolver import OutputResolver

    extension = (
        self.settings.file_format_settings.file_format
        if self.override_settings
        else project.settings_bake.file_format_settings.file_format
    )

    variables = get_variables(
        bake_group_name=bake_group.name,
        baker=self,
        image_name=self.image_name,
        packer=None,
        scene=bpy.context.scene,
        extension=extension,
    )

    filename = OutputResolver.resolve_filename(template, variables)

    if self.accumulated_image is not None:
        files = []
        if "<UDIM>" in self.accumulated_image.filepath_raw:
            p = Path(self.accumulated_image.filepath_raw)
            file_pattern = p.name.replace(".<UDIM>", "").split(".")[0]
            ext = p.suffix
            filepath = list(p.parent.glob(f"{file_pattern}*"))

            for f in filepath:
                files.append((f.parent, file_pattern, f.stem.replace(file_pattern, ""), ext))

            self.accumulated_image.filepath_raw = str(files[0][0] / (filename + ".<UDIM>" + files[0][3]))

        else:
            filepath = Path(self.accumulated_image.filepath_raw)
            file = (filepath.parent, filepath.name, "", filepath.suffix)
            files.append(file)

            self.accumulated_image.filepath_raw = str(file[0] / (filename + file[3]))

        for f in files:
            filepath = f[0] / (f[1] + f[2] + f[3])
            filepath.rename(filepath.with_name(filename + f[2] + f[3]))

        self.accumulated_image.name = filename

    from ..runtime.runtime_manager import RuntimeManager

    runtime = RuntimeManager.current(context)
    runtime.image_preview.update(self.accumulated_image, self.accumulated_uuid)

    from ..services.artifact_service import ArtifactService

    artifact = ArtifactService._find_property_group(
        project,
        bake_group.uuid,
        self.accumulated_producer_uuid,
        "ALL",
    )
    if artifact is None:
        LOG.debug(f"Artifact Not Found for {self.image_name} : Skip Renaming image")
        return

    runtime.outputs.invalidate(bake_group.uuid, self.accumulated_producer_uuid)
    runtime.outputs.clear_materialized(artifact.uuid)
    ArtifactService.rename_producer_filename(
        runtime,
        project,
        self.accumulated_producer_uuid,
        name=filename,
        filepath=self.accumulated_image.filepath_raw,
    )
    runtime.artifacts.rebuild()


def baker_items(self, context):
    from ..core.registry_baker import registry_baker

    return registry_baker.enum_items()


class UBK_BakerOutput(PropertyGroup):
    name: StringProperty("Object Name", default="")
    target_object_uuid: StringProperty()
    baker_uuid: StringProperty()
    image: PointerProperty(
        type=bpy.types.Image,
    )


class UBK_Baker(PropertyGroup):
    """One Bake Map"""

    uuid: StringProperty()

    enabled: BoolProperty(
        name="Enabled",
        default=True,
    )
    previewable: bpy.props.BoolProperty(name="Previewable", default=True)
    baker_settings: bpy.props.PointerProperty(type=UBK_BakerSettings)

    baker: EnumProperty(
        name="Bake Type",
        items=baker_items,
    )

    image_name: StringProperty(
        name="Image Name",
        default="Bake",
        update=update_image_name,
    )

    images: CollectionProperty(type=UBK_BakerOutput)

    accumulated_image: PointerProperty(type=bpy.types.Image)
    accumulated_producer_uuid: StringProperty()

    override_settings: BoolProperty(
        name="Override Settings",
        default=False,
    )

    settings: PointerProperty(
        type=UBK_BakeSettings,
    )

    override_settings_cage: BoolProperty(
        name="Override Cage",
        default=False,
    )

    custom_baker: PointerProperty(type=UBK_CustomBaker)

    @property
    def has_image(self) -> bool:
        return self.accumulated_image is not None

    @property
    def is_custom(self) -> bool:
        return self.baker.startswith("CUSTOM")

    @property
    def accumulated_uuid(self) -> str:
        if len(self.accumulated_producer_uuid) > 0:
            return self.accumulated_producer_uuid
        return self.uuid

    @accumulated_uuid.setter
    def accumulated_uuid(self, uuid: str) -> None:
        self.accumulated_producer_uuid = uuid

    # @property
    # def accumulated_image(self) -> bpy.types.Image:
    #     pass


classes = (
    UBK_BakerOutput,
    UBK_Baker,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
