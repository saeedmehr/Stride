from django.urls import path

# from web.views import WebView
from web.views import getProducts, getIndexedSites, getProductBrands, getBrands, getProductBrandsDetails, getProductDetails

urlpatterns = [
    path('sites', getIndexedSites, name="get_sites"),
    path('brands', getBrands, name="get_brands"),
    path('brands/<int:brandId>', getProductBrands, name="get_product_brands"),
    path('brands/<int:brandId>/details', getProductBrandsDetails, name="get_product_brands_details"),
    path('products/', getProducts, name="get_products"),
    path('products/<int:productId>', getProductDetails, name="get_product_details"),

]
