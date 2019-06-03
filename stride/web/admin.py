from django.contrib import admin
from web.models import TODO, Product,IndexedSite,Brand,ProductPosition

admin.site.register(TODO)
admin.site.register(Product)
admin.site.register(IndexedSite)
admin.site.register(Brand)
admin.site.register(ProductPosition)
