import pathlib
from .utils import bytes_to_mb
from rest_framework.serializers import ValidationError
from django.conf import settings


def validate_image_file(data):
    file_name = data.name
    file_size = data.size
    file_ext = pathlib.PurePosixPath(file_name).suffix.strip(".").lower()
    allowed_file_exts = ["png", "jpg", "jpeg"]
    if file_ext not in allowed_file_exts:
        raise ValidationError(
            f"Unsupported file extension, only supported {allowed_file_exts}"
        )
    max_allowed_size = settings.IMAGE_FILE_UPLOAD_MAX_SIZE
    if file_size > max_allowed_size:
        raise ValidationError(
            "File size should be less than %0.1f MB" % (bytes_to_mb(max_allowed_size))
        )
    return data