from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from users.serializers import UserGetSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngridientGetAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
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
    ingridients = IngridientGetAmountSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingridients',
                  'name',
                  'text',
                  'image',
                  'cooking_time')


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
