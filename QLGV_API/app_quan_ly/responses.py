from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


def success(**payload):
    return Response({"status": "success", **payload}, status=status.HTTP_200_OK)


def error(message, http_status):
    return Response({"status": "error", "message": message}, status=http_status)


class BaseListAPI(APIView):
    """GET: trả về toàn bộ bản ghi của `queryset` qua `serializer_class`"""
    queryset = None
    serializer_class = None

    def get(self, request):
        items = self.queryset.all()
        serializer = self.serializer_class(items, many=True)
        return success(total=len(serializer.data), data=serializer.data)
