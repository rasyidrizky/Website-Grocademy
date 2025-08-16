# utils.py
from django.core.paginator import Paginator, EmptyPage
from rest_framework.response import Response


class APIResponse:
    @staticmethod
    def success(message, data=None, pagination=None, http_status=200):
        payload = {
            "status": "success",
            "message": message,
            "data": data,
        }
        if pagination:
            payload["pagination"] = pagination
        return Response(payload, status=http_status)

    @staticmethod
    def error(message, data=None, http_status=400):
        payload = {
            "status": "error",
            "message": message,
            "data": data,
        }
        return Response(payload, status=http_status)


class PaginatorHelper:
    @staticmethod
    def paginate_queryset(
        queryset, request, serializer_cls,
        *, page_default=1, limit_default=15, limit_max=50, context=None
    ):
        try:
            page = int(request.query_params.get("page", page_default))
        except ValueError:
            page = page_default
        try:
            limit = int(request.query_params.get("limit", limit_default))
        except ValueError:
            limit = limit_default
        limit = min(max(limit, 1), limit_max)

        paginator = Paginator(queryset, limit)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages or 1)

        serializer = serializer_cls(page_obj.object_list, many=True, context=context)
        pagination = {
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
        }
        return serializer.data, pagination
