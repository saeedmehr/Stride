from django.core.management import BaseCommand
from django.db import transaction
from bs4 import BeautifulSoup
import json

from web.models import IndexedSite, Product, ProductPosition, Brand

"""
This class will handle parsing JSON from files. It'll add FILENAME as IndexedSite
Usage: ./manage.py scrape_sites JSON_FILE_NAME
Example: ./manage.py scrape_sites crawl_zalando.nl_2016-05-30T23-14-36.jl
The process is atomic and will discard changes if anything failed.
Site name will be determined from FILENAME
"""

bulk_products_data = []
bulk_products_positions_data = []

# Since brands are limited, it is worthy to cache them in memory
brands = {}
new_brands = []


class Competetions:
    ZALANDO = 'zalando.nl'
    OMODA = 'omoda.nl'
    ZIENGS = 'ziengs.nl'


def OMODA_parser(json_line, site_id):
    soup = BeautifulSoup(json_line['body'], features='lxml')  # lxml is installed in venv
    products_dom = soup.select('.products .artikel')
    products = []
    products_positions = []

    count_of_products_on_page = len(products_dom) + 1

    for i, p in enumerate(products_dom):
        img_addr = p.select('img.lazy')[0]['data-original']
        brand = p.select('.merk')[0].text
        title = p.select('img.lazy')[0]['alt']
        position_on_page = i + 1

        price = p.select(".prijs del")
        price_with_discount = None
        has_discount = False
        if price:
            price = price_to_float(price[0].text)
            has_discount = True
            price_with_discount = price_to_float(p.select(".prijs ins")[0].text)
        else:
            price = price_to_float(p.select(".prijs")[0].text)
        page_number = json_line['page_number']
        categories = ', '.join(json_line['product_category'])

        if brand not in brands:
            new_brands.append(brand)

        products.append(
            {
                # This `brand` is brand title not Its id, we'll map them late using dict with o(1)
                'brand_id': brand,

                # Saving title a composition of brand will will the title unique across different brands
                'title': "%s __ %s" % (brand, title)
            }
        )

        products_positions.append(
            ProductPosition(
                categories=categories,
                page_number=page_number,
                position_on_page=position_on_page,
                count_of_products_on_page=count_of_products_on_page,
                price=price,
                has_discount=has_discount,
                price_with_discount=price_with_discount,
                img_addr=img_addr,
                product_id="%s __ %s" % (brand, title),
                indexedSite_id=site_id
            )
        )

    return products, products_positions



def ZIENGS_parser(json_line, site_id):
    soup = BeautifulSoup(json_line['body'], features='lxml')  # lxml is installed in venv
    products_dom = soup.select('.products .artikel')
    products = []
    products_positions = []

    count_of_products_on_page = len(products_dom) + 1

    for i, p in enumerate(products_dom):
        img_addr = p.select('img.lazy')[0]['data-original']
        brand = p.select('.merk')[0].text
        title = p.select('img.lazy')[0]['alt']
        position_on_page = i + 1

        price = p.select(".prijs del")
        price_with_discount = None
        has_discount = False
        if price:
            price = price_to_float(price[0].text)
            has_discount = True
            price_with_discount = price_to_float(p.select(".prijs ins")[0].text)
        else:
            price = price_to_float(p.select(".prijs")[0].text)
        page_number = json_line['page_number']
        categories = ', '.join(json_line['product_category'])

        if brand not in brands:
            new_brands.append(brand)

        products.append(
            {
                # This `brand` is brand title not Its id, we'll map them late using dict with o(1)
                'brand_id': brand,

                # Saving title a composition of brand will will the title unique across different brands
                'title': "%s __ %s" % (brand, title)
            }
        )

        products_positions.append(
            ProductPosition(
                categories=categories,
                page_number=page_number,
                position_on_page=position_on_page,
                count_of_products_on_page=count_of_products_on_page,
                price=price,
                has_discount=has_discount,
                price_with_discount=price_with_discount,
                img_addr=img_addr,
                product_id="%s __ %s" % (brand, title),
                indexedSite_id=site_id
            )
        )

    return products, products_positions




def ZALANDO_parser(json_line, site_id):
    soup = BeautifulSoup(json_line['body'], features='lxml')  # lxml is installed in venv
    products_dom = soup.select('.catalogArticlesList li.catalogArticlesList_item')
    products = []
    products_positions = []

    count_of_products_on_page = len(products_dom) + 1

    for i, p in enumerate(products_dom):
        img_addr = p.select('img.catalogArticlesList_imageBoxImage')[0]['src']
        brand = p.select('.catalogArticlesList_brandName')[0].text
        title = p.select('.catalogArticlesList_articleName')[0].text
        position_on_page = i + 1
        prices = p.select(".catalogArticlesList_price")
        price = price_to_float(prices[0].text)
        price_with_discount = None
        has_discount = False
        page_number = json_line['page_number']
        categories = ', '.join(json_line['product_category'])

        # If there are two classes present with '.catalogArticlesList_price', There is a discount on product
        # Second instance is price with discount value
        if len(prices) == 2:
            has_discount = True
            price_with_discount = price_to_float(prices[1].text)

        if brand not in brands:
            new_brands.append(brand)

        products.append(
            {
                # This `brand` is brand title not Its id, we'll map them late using dict with o(1)
                'brand_id': brand,

                # Saving title a composition of brand will will the title unique across different brands
                'title': "%s __ %s" % (brand, title)
            }
        )

        products_positions.append(
            ProductPosition(
                categories=categories,
                page_number=page_number,
                position_on_page=position_on_page,
                count_of_products_on_page=count_of_products_on_page,
                price=price,
                has_discount=has_discount,
                price_with_discount=price_with_discount,
                img_addr=img_addr,
                product_id="%s __ %s" % (brand, title),
                indexedSite_id=site_id
            )
        )

    return products, products_positions


def price_to_float(price):
    # Moneys are in this format: '€ 123.45,67'
    # So we have to get rid of '€' and '.'.Then we have to replace ',' with '.' for floating point
    # They sometimes contain 'vanaf'

    float_str = price.lower()\
        .replace('€', '') \
        .replace('.', '') \
        .replace(',', '.') \
        .replace('vanaf', '') \
        .replace(' ', '')
    # I've removed 'vanaf' since there was nothing about handling it

    return float(float_str)


SITES = {
    Competetions.ZALANDO: ZALANDO_parser,
    Competetions.OMODA: OMODA_parser,
    Competetions.ZIENGS: ZIENGS_parser,
}


def json_reader(filename):
    # Read and parse each line as JSON, this will help in reading large files
    jsonfile = open(filename)
    while True:
        line = jsonfile.readline()
        if not line:
            break
        if 'product_listing' not in line:
            # We currently need only `product_listing` since it contains everything we want
            # This condition will not load json for `product_details` which improves performance
            continue
        yield json.loads(line)


def push_products(new_product_list, new_product_positions_list):
    global bulk_products_data
    global bulk_products_positions_data

    bulk_products_data += new_product_list
    bulk_products_positions_data += new_product_positions_list

    if len(bulk_products_positions_data) >= 100:

        # Add new brands to DB and cache them locally
        if len(new_brands) > 0:
            new_brands_created = []
            for n in new_brands:
                b, _ = Brand.objects.get_or_create(title=n)
                new_brands_created.append(b)

            for brand in new_brands_created:
                brands[brand.title] = brand.id

            new_brands.clear()

        # Iterate bulk data and set actual brand_id instead of brand_title
        for i, d in enumerate(bulk_products_data):
            bulk_products_data[i]['brand_id'] = brands[d['brand_id']]

        # Insert all products and ignore conflicts
        product_titles = []
        for n in bulk_products_data:
            Product.objects.get_or_create(**n)
            product_titles.append(n['title'])

        # Get all products related to ProductPositions model using their title
        related_products = Product.objects.filter(title__in=product_titles)
        products_title_dict = {rp.title: rp.id for rp in related_products}

        # Set productID for bulk_products_positions_data from related_products
        for i, prod_pos in enumerate(bulk_products_positions_data):
            bulk_products_positions_data[i].product_id = products_title_dict[prod_pos.product_id]

        # Insert all product positions and ignore conflicts
        ProductPosition.objects.bulk_create(bulk_products_positions_data, ignore_conflicts=True)

        bulk_products_data.clear()
        bulk_products_positions_data.clear()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file', help='Json file to parse')

    @transaction.atomic
    def handle(self, *args, **options):
        file_name = options['file']
        site_name = ''

        # Find site name in All indexed sites
        for site in SITES:
            if site in file_name.lower():
                site_name = site
                break

        # Use alias function for site_name, this will remove need of if statement in loop
        data_scraper = SITES[site_name]

        # Insert site name as indexed
        indexed_site, _ = IndexedSite.objects.get_or_create(domain=site_name)
        site_id = indexed_site.id

        # Cache current brand id and titles
        for brand in Brand.objects.all():
            brands[brand.title] = brand.id

        # TODO:
        #  If performance does matter more, we can use multiprocessing. The code is almost ready for this

        for json_line in json_reader(file_name):
            if json_line['page_type'] == 'product_detail':
                # Actually we dont need product_detail ! since all details we need are present in product_listing
                pass
            elif json_line['page_type'] == 'product_listing':
                products, products_positions = data_scraper(json_line, site_id)
                push_products(products, products_positions)
                # open('listing%s.html' % ii, 'w').write(json_line['body'])
            else:
                raise Exception("Unknown data found in json!")
