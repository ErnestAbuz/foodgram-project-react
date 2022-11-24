from rest_framework.pagination import PageNumberPagination


class ForPageNumberPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class SubsRecipeNumberPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'limit'
