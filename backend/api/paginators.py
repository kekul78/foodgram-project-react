from rest_framework.pagination import PageNumberPagination

import foodgram_backend.constants as const


class PagePagination(PageNumberPagination):
    page_size = const.PAGE_SIZE
    page_size_query_param = 'limit'
