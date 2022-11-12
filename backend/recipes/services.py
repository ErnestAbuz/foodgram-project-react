from rest_framework import status
from rest_framework.response import Response

PAGINATION_SIZE = 6


def add_or_del_obj(pk, request, param, data_for_validate):
    obj_bool = param.filter(pk=pk).exists()
    if request.method == 'DELETE' and obj_bool:
        param.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method == 'POST' and not obj_bool:
        param.add(pk)
        serialize = data_for_validate(
            param.get(pk=pk),
            context={'request': request}
        )
        return Response(serialize.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_shopping_list(ingredients):
    text_list = ['Список необходимых ингредиентов:\n']
    text_list += [
        f'{ingredient.get("ingredient__name").capitalize()} '
        f'({ingredient.get("ingredient__measurement_unit")}) - '
        f'{ingredient.get("sum_amount")}\n'
        for ingredient in list(ingredients)
    ]
    text_list += ['\n\nДанные проекта Foodgram']
    return text_list
