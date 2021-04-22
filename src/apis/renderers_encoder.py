from rest_framework.utils import encoders


class JSONEncoder(encoders.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError as e:
            if hasattr(obj, "to_json"):
                return obj.to_json()
            raise e
