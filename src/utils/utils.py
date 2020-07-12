from uuid import UUID

def verify_id(obj):
    return obj.id is not None and isinstance(obj.id, UUID) 