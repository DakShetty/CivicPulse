import os
from pathlib import Path
from flask import Blueprint, send_file, abort
from backend.services.storage_service import storage_service

storage_bp = Blueprint("storage", __name__, url_prefix="/api/v1/storage")


@storage_bp.route("/download/<path:object_key>", methods=["GET"])
def download_file(object_key: str):
    """Serves locally stored file attachments and reports safely."""
    # Prevent directory traversal
    clean_path = Path(os.path.normpath(object_key))
    if ".." in clean_path.parts:
        abort(400, "Invalid object key")

    local_path = storage_service.get_local_path(str(clean_path).replace("\\", "/"))
    if not local_path or not local_path.is_file():
        abort(404, "File not found")

    return send_file(local_path)
