from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from web.models import Product, IndexedSite, Brand
from web.serializers import ProductSerialize, IndexedSiteSerializer, BrandSerialize, ProductSerializerSimple


@api_view(['GET'])
def getBrands(request):
    brands = Brand.objects.all()
    paginator = PageNumberPagination()
    result_page = paginator.paginate_queryset(brands, request)
    serializer = BrandSerialize(result_page, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getProductBrands(request, brandId):
    b = Product.objects.filter(brand_id=brandId)
    paginator = PageNumberPagination()
    result_page = paginator.paginate_queryset(b, request)
    serializer = ProductSerializerSimple(result_page, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getProductBrandsDetails(request, brandId):
    b = Product.objects.filter(brand_id=brandId)
    paginator = PageNumberPagination()
    result_page = paginator.paginate_queryset(b, request)
    serializer = ProductSerialize(result_page, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getProductDetails(request, productId):
    print(productId)
    product = Product.objects.get(pk=productId)
    serializer = ProductSerialize(product, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getIndexedSites(request):
    indexed_sites = IndexedSite.objects.all()
    serialized = IndexedSiteSerializer(indexed_sites, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    paginator = PageNumberPagination()
    result_page = paginator.paginate_queryset(products, request)
    serializer = ProductSerialize(result_page, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)