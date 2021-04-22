from rest_framework.serializers import Serializer


class BaseSerializer(Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ViewRequestSerializer(BaseSerializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UpdateOnlySerializer(BaseSerializer):
    def create(self, validated_data):
        msg = (
            "'{}' is update only serializer, so you cannot perform "
            "`.create()` operation on it".format(self.__class__.__name__)
        )
        raise Exception(msg)