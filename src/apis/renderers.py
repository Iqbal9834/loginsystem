from rest_framework import renderers
from .renderers_encoder import encoders


class JSONRenderer(renderers.JSONRenderer):
    encoder_class = encoders.JSONEncoder
