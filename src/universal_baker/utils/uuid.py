import uuid


def ensure_uuid(prop):
    if not prop.uuid:
        prop.uuid = str(uuid.uuid4())
