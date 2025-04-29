import rest_framework.status as status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


# Create your views here.
def process_serializer(serializer_class, data, instance=None, success_status=status.HTTP_200_OK, create_status=status.HTTP_201_CREATED):
    serializer_instance = serializer_class(instance, data=data) if instance else serializer_class(data=data)
    if serializer_instance.is_valid():
        try:
            serializer_instance.save()
            return serializer_instance.data, (success_status if instance else create_status)
        except Exception as e:
            return {'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    return serializer_instance.errors, status.HTTP_400_BAD_REQUEST

def soft_delete_user(model, username):
    obj = get_object_or_404(model, username=username)
    obj.is_deleted = True
    obj.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
