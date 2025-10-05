from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class SmallPageNumberPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "limit"
    max_page_size = 100
    page_size = 10

    def get_paginated_response(self, data):
        current = self.page.number
        total_pages = self.page.paginator.num_pages
        count = self.page.paginator.count
        limit = self.get_page_size(self.request) or self.page.paginator.per_page
        next_page = current + 1 if self.page.has_next() else None
        prev_page = current - 1 if self.page.has_previous() else None

        return Response(OrderedDict([
            ("results", data),
            ("pagination", {
                "page": current,
                "limit": limit,
                "total_pages": total_pages,
                "total_count": count,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next_page": next_page,
                "previous_page": prev_page,
            }),
        ]))
