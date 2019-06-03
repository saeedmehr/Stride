from rest_framework import serializers

from web.models import TODO, IndexedSite, Brand, Product, ProductPosition


class TODOSerializer(serializers.Serializer):
    content = serializers.CharField()
    description = serializers.CharField()
    is_checked = serializers.BooleanField()

    class Meta:
        model = TODO
        fields = ['__all__']


class IndexedSiteSerializer(serializers.ModelSerializer):
    domain = serializers.CharField()

    class Meta:
        model = IndexedSite
        fields = ['id', 'domain']


class ProductPositionSerializer(serializers.ModelSerializer):
    categories = serializers.CharField()
    page_number = serializers.IntegerField()
    position_on_page = serializers.IntegerField()
    count_of_products_on_page = serializers.IntegerField()
    has_discount = serializers.BooleanField()
    price_with_discount = serializers.FloatField()
    img_addr = serializers.CharField()
    price = serializers.FloatField()
    indexedSite = IndexedSiteSerializer(read_only=True, many=False)

    class Meta:
        model = ProductPosition
        exclude = ('product',)


class ProductSerializerSimple(serializers.ModelSerializer):
    title = serializers.CharField()

    class Meta:
        model = Product
        exclude = ['brand']


class ProductSerialize(serializers.ModelSerializer):
    title = serializers.CharField()
    productPositions = ProductPositionSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = ['id', 'productPositions', 'title']


class BrandSerialize(serializers.ModelSerializer):
    title = serializers.CharField()
    class Meta:
        model = Brand
        fields = ['id', 'title']
