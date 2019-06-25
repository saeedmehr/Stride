# Stride

/web/sites -> Shows indexed sites list
/web/brands?page=1 -> Shows indexed brands ( with pagination)
/web/brands/<int:brandId>?page=1 -> Shows products of specific indexed brand ( with pagination)
/web/brands/<int:brandId>/details?page=1 -> Shows products of specific indexed brand with their positions and full details ( with pagination)

/web/products/?page=1 -> Shows products lists independently ( with pagination and details) 
/web/products/<int:productId> -> Shows product details of an product
