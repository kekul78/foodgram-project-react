from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
)
from users.serializers import CustomUserSerializer, UserGetSerializer
from users.models import MyUserModel


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngridientGetAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngridientCreateAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    @staticmethod
    def validate(data):
        if not Ingredient.objects.filter(pk=data['id']).exists():
            raise serializers.ValidationError(
                {'ingredients': 'Несуществующий ингредиент'}
            )
        return data

    @staticmethod
    def validate_amount(value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value


class RecipeGetSerializer(serializers.ModelSerializer):
    author = UserGetSerializer()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngridientGetAmountSerializer(many=True,
                                                read_only=True,
                                                source='recipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'text',
                  'image',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngridientCreateAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients',
                  'tags',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def validate(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredients')
        text = data.get('text')
        image = data.get('image')

        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Поле отсуствует'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Теги не уникальны'}
            )

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Поле отсутствует'}
            )
        unique_ingr = {item['id'] for item in ingredients}
        if len(unique_ingr) != len(ingredients):
            raise serializers.ValidationError(
                {'ingredients': 'Дублирование ингредиентов'}
            )

        if not text:
            raise serializers.ValidationError(
                {'text': 'Поле отсутствует'}
            )

        if not image:
            raise serializers.ValidationError(
                {'image': 'Нет картинки'}
            )

        return data

    def create_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create_ingredients(self, ingredients, recipe):
        for crutch in ingredients:
            id = crutch['id']
            ingredient = Ingredient.objects.get(pk=id)
            amount = crutch['amount']
            RecipeIngredient.objects.create(
                ingredients=ingredient, recipe=recipe, amount=amount
            )

    def create(self, validated_data):

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        user = self.context.get('request').user

        recipe = Recipe.objects.create(
            **validated_data,
            author=user,
        )
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):

        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.get('tags', None)

        if tags is None:
            raise serializers.ValidationError('А создавать без тегов ни-ни!')

        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.tags.clear()
        self.create_tags(tags, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeGetSerializer(instance).data


class FavoriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MyUserModel
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()
