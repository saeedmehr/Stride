from django.db import models


class TODO(models.Model):
    content = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name='Title')
    description = models.TextField(blank=True)
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.content)


class IndexedSite(models.Model):
    domain = models.CharField(max_length=255, unique=True, verbose_name='Indexed Site')

    def __str__(self):
        return "{}".format(self.domain)


class Brand(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name='Brand Name')

    # logo = models.CharField(max_length=255, unique=True, null=True, blank=True, default='/img/defaultlogo.png')

    def __str__(self):
        return "{}".format(self.title)


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Product Name', db_index=True)
    brand = models.ForeignKey(Brand, on_delete=None, related_name='brand', db_index=True)

    class Meta:
        unique_together = ('title', 'brand',)

    def __str__(self):
        return "{}".format(self.title)


class ProductPosition(models.Model):
    categories = models.CharField(max_length=1000, null=True, blank=True)

    page_number = models.PositiveIntegerField()

    position_on_page = models.PositiveIntegerField()

    count_of_products_on_page = models.PositiveIntegerField()
    price = models.FloatField()  # Price might be different on different sites
    has_discount = models.BooleanField(default=False)
    price_with_discount = models.FloatField(blank=True, null=True)
    img_addr = models.CharField(max_length=1000, default='/img/default.png')
    indexedSite = models.ForeignKey(IndexedSite, on_delete=None, related_name='indexedSite')
    product = models.ForeignKey(Product, on_delete=None, related_name='productPositions', db_index=True)

    class Meta:
        unique_together = (
        'categories', 'page_number', 'position_on_page', 'count_of_products_on_page', 'indexedSite', 'product',
        'indexedSite', 'price', 'has_discount',)
