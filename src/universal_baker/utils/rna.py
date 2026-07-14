def copy_rna(src, dst):
    for prop in src.bl_rna.properties:
        if prop.is_readonly:
            continue

        identifier = prop.identifier

        try:
            setattr(
                dst,
                identifier,
                getattr(src, identifier),
            )
        except:
            pass
