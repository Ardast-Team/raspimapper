cd ~/Documents/Projects
pip install pip --upgrade
pip install django
django-admin startproject mapper2
cd mapper2

python3 -m venv venv
source venv/bin/activate
pip install pip --upgrade
pip install django

# RabbitMQ(broker)
sudo docker run -d -p 5672:5672 rabbitmq

# CELERY
pip install celery
pip install django-celery-results
create celery.py
include in __init__.py
include in setting.py
create task.py inside each app in project
python manage.py migrate django_celery_results



# DJANGO COURSE

PaXQCAJRs9V9C3b

## Client/Server

    CLIENT: React, Angular, Vue -> Frontend
    SERVER: Django, ASP.NET, Express -> Backend

## Environment

```bash
pip install --upgrade pip
pip install --upgrade wheel
pip install --upgrade setuptools
pip install --upgrade requests

pip install pipenv
pipenv install
```

or

```bash
sudo apt install python3.10-venv
python3 -m venv .
pipenv install django
django-admin startproject <myproject> .
```

python manage.py **command**:

```bash
python manage.py startapp **myapp**
python manage.py runserver
```

In **myapp** create "urls.py":

```python
from django.urls import path
from . import views
```

in **myapp** create a folder called "templates"

## Debug Toolbar

```python
pipenv install django-debug-toolbar
```

In **settings.py**:

In **INSTALLED_APPS** insert:

    'debug_toolbar'

In **MIDDLEWARE** insert:

    'debug_toolbar.middleware.DebugToolbarMiddleware'

Insert **INTERNAL_IPS**:

```python
INTERNAL_IPS = [
    '127.0.0.1',
]
```

In **urls.py** of the **Project** insert:

```python
path('__debug__/', include(debug_toolbar.urls))
```

To createa new Admin User:

```bash
python manage.py createsuperuser
```

## MODELS

### Relationship

    - 1 to 1
    - 1 to N
    - N to N

### Django Field types

https://docs.djangoproject.com/en/4.1/ref/models/fields/

### One To One Relationship

Used to link a child class to the Parent

Needs to be specified the "on_delete" inside the child:

    - **CASCADE** -> If the Parent is deleted, then the child where the OneToOne field is defined is also deleted
    - **SET_NULL** -> The child is going to stay in the database but all the fields will be set to Null
    - **SET_DEFAULT** -> Each child field wll be set to its Default value
    - **PROTECT** -> Avoid Parent deletion if a child exist

If there's a 1 to 1 relationship between Parent and Child, **"primary_key=True"** needs to be set

### One to Many Relationship

We use **"models.ForeignKey"** in the Child to reference to a model that allow multiple childs for a certain parent

### Many To Many Relationship

We use "models.ManyToManyField" in the Child to reference to a model that allow multiple childs for multiple parents, you can specify the "related_name" of the key that is created inside the Parent to reference to the N possible Child

### Circular dependency

If I have a parent containing a reference to a unique child (like a featured/starred child), we need to create a referencie into the Parent class to the child.
This create a ciscular dependency, the child have a reference to the parend and the Parent have a reference to the child.
You crate a **"models.ForeignKey"** inside the Partent to reference to the child.
When you create a reference, django create the reverse-relationship too which may lead to name clashes if you used the Parent name as referenced name into the child.
Possible solutions:

    - On the Parent reference, indicate a "related_name" attirbute to avoid classhes in the reverse-relationship
    - On the Parent reference, indicate a "related_name='+' " attirbute to avoid Django to produce the reverse-relationship (if you're not interested in reference this dependency into the child. Which is normally the situation you'll be into)

### Generic Relationship between elements of different apps

In **models.py**:

```python
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
```

in each class that link to an item of aonother app:

```python
content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
object_id = models.PositiveIntegerField()
content_object = GenericForeignKey()
```

## Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Customizing database schema

Include class "Meta" to a certain model.

    https://docs.djangoproject.com/en/4.1/ref/models/options/

### Revert Migration

```bash
python manage.py migrate **myapp** **last_correct_migration_number**
```

## MySQL

### Install

```bash
sudo mysql

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password by 'mynewpassword';

quit

sudo mysql_secure_installation
```

user: root

pwd zampasport4ever

### access to shell

```bash
sudo mysql -p
```

### Install MySQL Workbench

```bash
sudo snap install mysql-workbench-community
snap connect mysql-workbench-community:password-manager-service
snap connect mysql-workbench-community:ssh-keys
```

### Install mysqlclient on Pipenv to access to MySQL DB

```bash
sudo apt install default-libmysqlclient-dev
pipenv install mysqlclient
```

## Config MySQL as Engine

In "setting.py":

```python
    ## MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '<DB_NAME>',
            'HOST': 'localhost',
            'USER': 'root',
            'PASSWORD': '<ROOT_PWD>'
        }
    }
```

## SQL Custom Query

### Create empty Migration

python manage.py makemigrations **myapp** --empty

### Inclufe Custom SQL code

```python
operations = [
        migrations.RunSQL(
            # Include custom SQL statement
            """
            INSERT INTO store_collection (title)
            VALUES ('collection1')
            """,
            # If previous statement fails, revert (because we cannot undo the migration using custom SQL if it fails)
            """
            DELETE FROM store_collection
            WHERE title='collection1'
            """)
    ]
```

### Create Dummy Data

Go to www.mockaroo.com

    Date in format YYYY-MM-DD

## MANAGERS and QuerySets

It's used in the **views.py**

The "Objects" method is  used as an SQL Manager and returns a QuerySet:

```python
query_set = Product.objects.all()
```

The QuerySet is then evaluated as an SQL Query when:

1. it's Iterated:

```python
for product in query_set:
    print(product)

```

2. It's converted to a List:

```python
list (query_set)
```

3. an element or to a Slice of the QuerySet is accessed:

```python
query_set[0]
query_set[0:5]
```

Advance queries:

```python
query_set.filter().filter().order_by()
```

Methods that evaluate SQL immediatelly:

```python
*.objects.count()
*.objects.get(pk=1)
*.objects.filter(pk=1).first()
*.objects.filter(pk=1).exists()
*.objects.earliest('unit_price') #Ordered by unit price
*.objects.latest('unit_price')	#Ordered by unit price
```

### Filter

Filter method needs the paraemter to be a Boolean value:

    CORRECT: *.objects.filter(pk=1)
    ERROR:   *.objects.filter(pk>1)

To be able to generate Logic such as *greater than* or *ess than* we need to use special termination of a certain variable:

    GREATER THAN:           *.objects.filter(pk__gt=1)
    GREATER OR EQUAL THAN:  *.objects.filter(pk__gte=1)
    LESS THAN:              *.objects.filter(pk__lt=1)
    LESS OR EQUAL THAN:     *.objects.filter(pk__lte=1)

Other terminations:

    exact
    contains
    in
    startswith
    endswith
    range
    date
    isnull
    regex


### Complex filter across relationship:

*.objects.filter(**RelatedTable**__**Attribute**__**lookup**)

```python
Product.objects.filter(collection__id__range=(1,5))
```

### Best practice

Always wrap on a Try-Catch when trying to retrieve data with **get**:

```python
from django.core.exceptions import ObjectDoesNotExist

try:
    product = Product.objects.get(pk=0)
except ObjectoesNotExist:
    pass
```

***

## Complex Lookups

***

### AND Operator

inventory < 10 AND unit_price < 20

Filters:

```python
*objects.filter(inventory__lt=10, unit_price__lt=20) # One filter
*objects.filter(inventory__lt=10).filter(unit_price__lt=20) #2 separate filters
```

### OR Operator

inventory < 10 AND unit_price < 20

We need to use Q Object

```python
from django.db.models import Q

*objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))
```

Q Objects can be linked by logical operator **&** (AND), **|** (OR), **~** (NOT)

### Reference 2 fields with F Objects

inventory = unit_price

```python
*.objects.filter(inventory=F('unit_price'))
```

### Sorting

```python
*.objects.order_by('unit_price','-title').reverse()
```

#### Limiting

```python
*.objects.all()[:5] #LIMIT 5
*.objects.all()[4:] #OFFSET 4
*.objects.all()[3:12] #OFFSET 3 LIMIT 9
```

In General, for a Slice like [X,Y]

    OFFSET X
    LIMIT Y-X

### Querying just some Fileds

Use **Value** method to SELECT just some fields

```python
*.objects.values('id','title') 
```
```sql
-> SELECT id,title FROM ...
```

Reading a Related field

```python
Products.objects.values('id','title','collection__title') 
```
```sql
-> SELECT product.id,product.title,collection.title FROM product INNER JOIN collection ON (product.collection_id=collection.id)
```

Using the **values()** method we receive a Dictionary (not a queryset of Product instance).

    Ex: {id: 1, title: MyTitle, collection_title: MyCollection}

Using the **values_list()** method we receive a bunch of tupples.

    Ex: (1, MyTitle, MyCollection)

Avoid Duplicate with **distinct()**

```python
OrderItem.objects.values('product_id').distinct()
```

Nest Querysets filter:

```python
queryset = Product.objects.filter(
    id__in = OrderItem.objects.values('product_id').distinct()
).order_by('title')
```

Using the **only()** methods instead of **values()** we'll receive an Object instance instead of a Dictionary
The **only()** method is used to retrieve a query with only the fieds indicated

```python
*.objects.only('id','title')
```

IMPORTANT:
with the **only()** method you might end having a lot of extra query if you're consulting a property that is not returned inside the object queryset you're asking for (for example if in the case above you ask for render the UnitPrice which is not asked in the Only method). In this case for each ID the Only() method will ask for the Unit Price method of that particular ID in a separate Query, slowing down the execution

For a Template like:

```html
<ul>
    {% for product in products %}
    <li>{{ product.title }} ${{ product.unit_price }}</li>
    {% endfor %}
</ul>
```

we need a queryset like:

```python
query_set = Product.objects.only('id', 'title', 'unit_price').order_by('title')
```

```sql
-> SELECT id,title, unit_price FROM products
```

not like

```python
query_set = Product.objects.only('id', 'title')
```

```sql
-> SELECT id,title FROM products
-> SELECT id,unit_price FROM products where products.id = 1
-> SELECT id,unit_price FROM products where products.id = 2
-> SELECT id,unit_price FROM products where products.id = 3
-> [...]
```

The **defer()** method does the exact opposite of the **only()** method
Using the **defer()** methods will return an object instance with all the fields except the ones indicated:

```python
query_set = Product.objects.defer('description')
```

```sql
-> SELECT id,title,slug,unit_price,inventory,last_update,collection,promotions FROM products
```

### Selecting Related Objects:

Using the **select_related()** method will generate a query including the table related to the selected field

```python
query_set = Product.objects.select_related('collection').all()
```
```sql
-> SELECT * FROM product INNER JOIN collection ON (product.collection_id = collection.id)
```

IMPORTANT:
we use **select_related()** when the relationship with the related object is 1 (a certain Product belong to 1 Collection) [normally when we use a **ForeignKey()** in the model]
we use **prefetch_related()** when the relationship with the related object is N (a certain Product can belong to N Promotions) [normally when we use a **ManyToManyField()** in the model or when we have to refer to the Reverse relationship of a Foreigh key (ex. refer to the OrderItems when cosulting the Order as N OrderItems are present for an Order)]

```python
query_set = Product.objects.select_related('promotions').all()
```

```sql
-> SELECT * FROM product
-> SELECT * FROM promotion INNER JOIN product_promotions ON (promotions.id=product_promotions.promotion_id)
```

We can also comine Prefetch and Select:

```python
query_set = Product.objects.select_related('promotions').select_related('collection').all()
```

EXERCISE:
Get last 5 orders with their customer and items (including products)

```python
# STEP 1: Get the Orders and the relative Customer, sort by date and slice for the top 5 values
query_set = Order.objects.select_related('customer').order_by('-placed_at')[:5]
```
```sql
-> SELECT * FROM order INNER JOIN customer ON (order.customer_id = customer.id)
```
```python
# STEP 2: Preload the OrderItems of each Order by using default Reverse relation field "orderitem_set"
    query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set').order_by('-placed_at')[:5]
```
```sql
-> SELECT * FROM order INNER JOIN customer ON (order.customer_id = customer.id)
-> SELECT * FROM orderitem WHERE orderitem.order_id IN (**first 5 values**)
```
```python
# STEP 3: In the preload, span the relationship to the Product related to each OrderItem
    query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
```
```sql
-> SELECT * FROM order INNER JOIN customer ON (order.customer_id = customer.id)
-> SELECT * FROM orderitem WHERE orderitem.order_id IN (**first 5 orders**)
-> SELECT * FROM product WHERE product.id IN (**order items previously queried**)
```

### Aggregates

In order to have statistical info: COUNT, MAX, AVG, SUM

```python
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
```

**Count()** will count the nº of occurrences of the field that are not NULL. It will return a dictionary.

```python
result = Product.objects.aggregate(Count('id'), Min('unit_price'))
```
```json
-> return = {'id__count' : '1000', 'unit_price__min' : '10' } 
```
```python
result = Product.objects.aggregate(count=Count('id'), min_price=Min('unit_price'))
```
```json
-> return = {'count' : '1000', 'min_price' : '10'}
```

Exercises:

How many orders do we have?

```python
orders_numbers = Order.objects.aggregate(count=Count('id'))
```

How many units of product 1 have we sold?

```python
sum_qty_prod_1_ordered = OrderItem.objects.filter(product__id=1).aggregate(sum=Sum('quantity'))
```

How many orders has customer 1 placed?

```python
orders_cust_1 = Order.objects.filter(customer__id=1).aggregate(count=Count('id'))
```

What is the min, max and average price of the products in collection 3?

```python
min_price_coll_3 = Product.objects.filter(collection__id=3).aggregate(min=Min('unit_price'))
max_price_coll_3 = Product.objects.filter(collection__id=3).aggregate(max=Max('unit_price'))
avg_price_coll_3 = Product.objects.filter(collection__id=3).aggregate(avg=Avg('unit_price'))
```

### Annotating Objects

**Annotate()** is used as an AS in SQL Query to store an extra column in the queryset according to specific criteria. It acept just Expression Classes
**Value()** , **F()** , **Func()**, **Aggrgate()** all return an Expression Class:

**Value()**  is used for representing simple values (Boolean, Numbers, String)
**F()** is used for referencing a field
**Func()** is used for calling DB functions
**Aggrgate()** is used for all aggregate functions (such as count, sum, min, max, avg, ...)
**ExpressionWrapper()** is used for Complex expresisons (see separate section)

```python
from django.db.models import Value, F, Func, ExpressionWrapper

annotation_query_set = Customer.objects.annotate(is_new=Value(True))
```
```sql
-> SELECT id,..., 1 AS is_new FROM customer
```
```python
annotation_query_set = Customer.objects.annotate(new_id=F('id') + 1)
```
```sql
-> SELECT id ,..., (id + 1) AS new_id FROM customer
```
```python
annotation_query_set = Customer.objects.annotate(
    full_name=Func(F('first_name'), F('last_name'), Value(' '),function='CONCAT')
```
```sql
-> SELECT id ,..., CONCAT(first_name, ' ', last_name) AS full_name FROM customer
```

ALTERNATIVE USING [DB FUNCTIONS](https://docs.djangoproject.com/en/4.1/ref/models/database-functions/) :

```python
from django.db.models.functions import Concat

full_name= Concat('first_name',Value(' '),'last_name')
```

### Grouping Data

```python
orders_count_per_customer = Customer.objects.annotate(
    orders_count=Count('order')
    )
```
```sql    
-> SELECT, id,..., COUNT(order.id`) AS orders_count FROM customer LEFT OUTER JOIN order ON (customer.id = order.customer_id) GROUP BY customer.id
```

IMPORTANT: There's a LEF OUTER JOIN because not all the customers have an Order

### EXPRESSION WRAPPER

Used to correctly output the type in case of an operation where there are mixed types
F('unit_price') -> Return a DecimalField() object
0.8 -> Returns a FloatField() object
You have to fix the Output, otherwise you'll receive an error


discounted_price = ExpressionWrapper(
    F('unit_price') * 0.8, output_field=DecimalField()
)
queryset = Product.objects.annotate(
    discounted_price=discounted_price
)

EXERCISE:

1. Customers with their last order ID

```python
#Python:
customer_with_last_order = ExpressionWrapper(
    Func(F('last_name'),Value (' '),F('first_name'),Value (' - '),F('last_order'),function='CONCAT'), 
    output_field=CharField()
)

#1. Filter for customer with Not Null Order set
#2. Join all the orders for each customer and show the max value of Placed_at grouping for customer
#3. include ExpressionWrapper column
#4. Order by last_order
customer_with_last_order_query = Customer.objects.filter(order__isnull=False).annotate(
    last_order=Max('order__placed_at'), #Show Order.PlacedGrouping
    customer_with_last_order=customer_with_last_order #ExpressionWrapper
).order_by('-last_order')
```
```sql
#SQL:
SELECT `store_customer`.`id`,
    `store_customer`.`first_name`,
    `store_customer`.`last_name`,
    `store_customer`.`email`,
    `store_customer`.`phone`,
    `store_customer`.`birth_date`,
    `store_customer`.`membership`,
    MAX(`store_order`.`placed_at`) AS `last_order`,
    CONCAT(`store_customer`.`last_name`, ' ', `store_customer`.`first_name`, ' - ', MAX(`store_order`.`placed_at`)) AS `customer_with_last_order`
FROM `store_customer`
INNER JOIN `store_order`
    ON (`store_customer`.`id` = `store_order`.`customer_id`)
WHERE `store_order`.`id` IS NOT NULL
GROUP BY `store_customer`.`id`
ORDER BY `last_order` DESC
```

2. Collections and count of their products 
```python
#python:
collection_count = Collection.objects.annotate(
    count=Count('product')
)
```
```sql
#SQL:
SELECT `store_collection`.`id`,
    `store_collection`.`title`,
    `store_collection`.`featured_product_id`,
    COUNT(`store_product`.`id`) AS `count`
FROM `store_collection`
LEFT OUTER JOIN `store_product`
    ON (`store_collection`.`id` = `store_product`.`collection_id`)
GROUP BY `store_collection`.`id`
ORDER BY NULL
```

3. Customers with more than 5 orders

```python
#Python:
#1. Filter for customer with Not Null Order set
#2. Join all the orders for each customer and fiter for the ones with OrderCount >5 and grouping for customer
customer_with_more_than_5_orders = Customer.objects.annotate(
    order_count=Count('order__customer')
).filter(order_count__gt=5)
```
```sql
SELECT `store_customer`.`id`,
    `store_customer`.`first_name`,
    `store_customer`.`last_name`,
    `store_customer`.`email`,
    `store_customer`.`phone`,
    `store_customer`.`birth_date`,
    `store_customer`.`membership`,
    COUNT(`store_order`.`customer_id`) AS `order_count`
FROM `store_customer`
LEFT OUTER JOIN `store_order`
ON (`store_customer`.`id` = `store_order`.`customer_id`)
GROUP BY `store_customer`.`id`
HAVING COUNT(`store_order`.`customer_id`) > 5
ORDER BY NULL
```

4. Customers and the total amount they’ve spent

```python
total_amount = ExpressionWrapper(
    Sum(F('order__orderitem__quantity') * F('order__orderitem__unit_price')),
    output_field=DecimalField()
)
customer_and_total_amount = Customer.objects.annotate(
    total_amount=total_amount  
)
```
```sql
SELECT `store_customer`.`id`,
    `store_customer`.`first_name`,
    `store_customer`.`last_name`,
    `store_customer`.`email`,
    `store_customer`.`phone`,
    `store_customer`.`birth_date`,
    `store_customer`.`membership`,
    SUM((`store_orderitem`.`quantity` * `store_orderitem`.`unit_price`)) AS `total_amount`
FROM `store_customer`
LEFT OUTER JOIN `store_order`
ON (`store_customer`.`id` = `store_order`.`customer_id`)
LEFT OUTER JOIN `store_orderitem`
ON (`store_order`.`id` = `store_orderitem`.`order_id`)
GROUP BY `store_customer`.`id`
ORDER BY NULL
```


5. Top 5 best-selling products and their total sales

```python
#Python:
best_5_product_and_sales = Product.objects.annotate(
    total_sales=Sum(F('orderitem__unit_price')*F('orderitem__quantity'))
).order_by('-total_sales')[:5]
```
```sql
#SQL:
SELECT `store_product`.`id`,
    `store_product`.`title`,
    `store_product`.`slug`,
    `store_product`.`description`,
    `store_product`.`unit_price`,
    `store_product`.`inventory`,
    `store_product`.`last_update`,
    `store_product`.`collection_id`,
    SUM((`store_orderitem`.`unit_price` * `store_orderitem`.`quantity`)) AS `total_sales`
FROM `store_product`
LEFT OUTER JOIN `store_orderitem`
ON (`store_product`.`id` = `store_orderitem`.`product_id`)
GROUP BY `store_product`.`id`
ORDER BY `total_sales` DESC
LIMIT 5
```

### Querying Generic Relationships

Querying relationships

```python
    from tags.models import Tag, TaggedItem
    from django.contrib.contenttypes.models import ContentType

    #Generic Relationship between Product and Tags
    content_type = ContentType.objects.get_for_model(Product)

    tags_queryset = TaggedItem.objects.select_related('tag').filter(
        content_type=content_type,
        object_id=1 #Product ID, should be calculated dynamically according to the URL
    )
```
```sql
    SELECT `tags_taggeditem`.`id`,
        `tags_taggeditem`.`tag_id`,
        `tags_taggeditem`.`content_type_id`,
        `tags_taggeditem`.`object_id`,
        `tags_tag`.`id`,
        `tags_tag`.`label`
    FROM `tags_taggeditem`
    INNER JOIN `tags_tag`
    ON (`tags_taggeditem`.`tag_id` = `tags_tag`.`id`)
    WHERE (`tags_taggeditem`.`content_type_id` = 11 AND `tags_taggeditem`.`object_id` = 1)
```

### Custom Managers

In tags\models.py:

```python
    class TaggedItemManager(models.Manager):
    def get_tags_for(self, obj_type, obj_id):
        content_type = ContentType.objects.get_for_model(obj_type)
        return TaggedItem.objects.select_related('tag').filter(
        content_type=content_type,
        object_id=obj_id #Product ID, should be calculated dynamically according to the URL
        )

    class TaggedItem(models.Model):
        objects = TaggedItemManager() #Doing this I'm overwriting the objects with our Custom Manager instance
        tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
        content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
        object_id = models.PositiveIntegerField()
        content_object = GenericForeignKey()
```

in this way I can use the following method:

```python
    TaggedItem.get_tags_for(Product,1)
```

### Caching mechanism

Query evaluation:

```python
    queryset = Product.objects.all()
    list(queryset)  # 1º iteration -> Evaluated and Cached
    list(queryset)  # 2º iteration -> Not Evaluated, Read from Cache
    queryset[0]     # Individ elem -> Not Evaluated, Read from Cache
```

### Creating objects

Use the **save()** method to INSERT into Database

```python
    #INSERT
    collection = Collection()
    collection.title = 'Video Games'
    collection.featured_product = Product(id=1)
    collection.save()
```
```sql
    -> INSERT INTO `store_collection` (`title`, `featured_product_id`)
    VALUES ('Video Games', 1)
```
```python
    #UPDATE
    collection = Collection.objects.get(pk=11)
    collection.title = 'Games'
    collection.featured_product = None
    collection.save()
```
```sql
    -> UPDATE `store_collection`
    SET `title` = 'Games',
        `featured_product_id` = NULL
    WHERE `store_collection`.`id` = 11
```

We also have direct methods (but makes your code more fragile):

```python
    Collection.objects.create(featured_product=None)
    Collection.objects.filter(pk=11).update(featured_product=None)
```

We can call the **delete()** method to delete an object

```python
    collection = Collection(pk=11)
    collection.delete()
```

or with the relative direct method (used also to delete multiple objects trough the filtes)

```python
    Collection.objects.filter(id__gt=5).delete()
```

EXERCISES:

•Create a shopping cart with an item

```python
    cart = Cart()
    cart.save()
```
```sql
    -> INSERT INTO `store_cart` (`created_at`)
    VALUES ('2022-10-22 11:05:41.819548')
```
```python
    cart_item = CartItem()
    cart_item.cart = cart
    cart_item.product = Product(id=1)
    cart_item.quantity = '10'
    cart_item.save()
```
```sql
    -> INSERT INTO `store_cartitem` (`cart_id`, `product_id`, `quantity`)
    VALUES (1, 1, 10)
```

•Update the quantity of an item in a shopping cart

```python
    cart_item2 = CartItem.objects.get(pk=1)
    cart_item2.quantity = '20'
    cart_item2.save()
```
```sql
    -> UPDATE `store_cartitem`
    SET `cart_id` = 1,
       `product_id` = 1,
       `quantity` = 20
    WHERE `store_cartitem`.`id` = 1
```

•Remove a shopping cart with its items

```python
    cart.delete()
    cart.save()
```
```sql
    -> DELETE FROM `store_cartitem`
    WHERE `store_cartitem`.`cart_id` IN (3)
    -> DELETE FROM `store_cart`
    WHERE `store_cart`.`id` IN (3)
```

### TRANSACTIONS

We can wrap operation into 1 transaction in order to avoid inconsistencies in case the generation between Parent-child goes wrong.
We use the  **@transaction.atomic()** decorator to wrap a certain **def**

```python
    from django.db import transaction

    @transaction.atomic()
    def say_hello(request)
```

If you want more control on what's beeing executed inside the Transaction you can use the **transaction.atomic()** as a **ContextManager()** and wrap it inside a **with** block

```python
    with transaction.atomic():
     [...]
```

### Raw Queries in SQL

 To write raw SQL queries use the **raw()** method

```python
    queryset = Product.objects.raw('SELECT * FROM store_product')
```

Sometimes we want to  execute queries that don't map to our model objects.
We can acces the DB directy and bypass the Model Layer

```python
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute('SELECT * ')
    cursor close()
```

or

```python
    with connection.cursor() as cursor:
        cursor.execute('SELECT * ')
```

To execute Store Procedures:

```python
    with connection.cursor() as cursor:
        cursor.callproc('get_customers', [1,2,'a'])
```

## ADMIN SITE
 
 To register an App to the Admin you have to edit the **admin.py**

```python
    from . import models

    admin.site.register(models.Collection)
```

To see the correct Name I have to use the **__str__** def inside the Class in **models,py**

```python
        def __str__(self) -> str:
        return self.title
```

To order the items you have to use **Meta** Class inside the Class in **models,py**

```python
        class Meta:
        ordering = ['title']
```

### Customize List Page

In **admin.py** create the class *Admin (ej ProductAdmin)

```python
    @admin.register(models.Product)
    class ProductAdmin(admin.ModelAdmin):
        list_display = ['title','unit_price']
        list_editable = ['unit_price']
        ordering = ['unit_price']
        list_per_page = 10
```

in this way you dont need anymore the ```admin.site.register(models.Product)```

For the complete list: [Django ModelAdmin](https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#modeladmin-options)

To add Computed Columns you can create a *Def* and add it to the *list_display*:

```python
    @admin.register(models.Product)
    class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','unit_price','inventory_status']
    list_editable = ['unit_price']
    list_per_page = 10

    def inventory_status(self, product):
        if product.inventory < 10
            return 'Low'
        return 'OK'
```

By deault the new column is nost sortable because Django doesn't know how to sort it.
To do so we need to specify the decorator **@admin.display(ordering='inventory')**:

```python
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10
            return 'Low'
        return 'OK'
```

To select Related objects you can easily include the related field in the *list_display*

```python
class ProductAdmin(admin.ModelAdmin):

    list_display = ['title','unit_price','inventory_status', 'collection']
```

in this case it will appear the default representation or the one overwrited with the relative **__str__** magic method

If we want to create a custom behaviour asociated to a related field, we need to ensure that the related field is previously SELECTED to avoid undesired SQL queries:

```python
    @admin.register(models.Product)
    class ProductAdmin(admin.ModelAdmin):
        list_display = ['title','unit_price','inventory_status', 'collection_title']
        list_editable = ['unit_price']
        ordering = ['unit_price']
        list_per_page = 10
        list_select_related = ['collection']

        def collection_title(sef, product):
            return product.collection.title
```

To annotate a new Computed column into the ADMIN SITE we can overwrite the **get_queryset()** def:

```python

from django.db.models import Count
[...]
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id','title','featured_product','products_count']
    list_editable = ['title']
    ordering = ['title']
    list_per_page = 10

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        return collection.products_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )
```

To create links to another TAB and Filtering it tho check just specified elements:

```python
from django.utils.html import format_html
from django.urls import reverse
[...]
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id','title','featured_product','products_count']
    list_editable = ['title']
    ordering = ['title']
    list_per_page = 10

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        #reverse(admin:app_model_page)
        url = (
                    reverse('admin:store_product_changelist') #This returns the Product url tab
                    #We then need to extend the url to filter the Product tab related to the collection id selected
                    + '?'
                    +urlencode({
                        'collection__id': collection.id
                    })
                )
        return format_html('<a href="{}">{}</a>',url , collection.products_count) #This creates the url Link to products_count 

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )
```

To add the search to the list page use the **search_fields** array:

```python
    search_fields = ['last_name__istartswith'] #the search string use the lookup "istartswith" 
```

To add the search to the list page use the **list_filter** array:

```python
    list_filter = ['collection']
```
to create customer filters, create a class and use it as part of the **list_filter**:

```python
#Custom filter
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory' # Name of the fitler
    parameter_name = 'inventory' #Parameter that will appear in the Url query

    def lookups(self, request, model_admin):
        return [
            # Tupples containing Value1 (the value included in the Url query), Value2 (the Name that will appear in the filter)
            ('<10','Low'),
            ('>10','OK')  
        ]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10) # queryset returned from the filter
        if self.value() == '>10':
            return queryset.filter(inventory__gte=10) # queryset returned from the filter
```

 then:

```python
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','title','unit_price','inventory_status', 'collection_title']
    list_editable = ['unit_price']
    ordering = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title__istartswith']
    list_filter = ['collection','last_update', InventoryFilter]
```

Defining custom actions:

```python
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    [...]

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset): #The queryset refers to the records selected by the user
        updated_count = queryset.update(inventory=0) #This will return the number of updated records
        #show up message
        self.message_user(
            request,
            f'{updated_count} products were successfully updated',
            #messages.WARNING
            #messages.ERROR
            messages.SUCCESS
        )
```

### Customizing form

set **fields**, **exclude** or **readonly_fields**

```python
fields = ['title']
exclude = ['title']
readonly_fields = ['title']
```

use **prepopulated_fields**

```python
prepopulated_fields = {
    'slug':['title','id']
}
```

use **autocomplete_fields**

```python
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
[...]

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields = ['title'] # Django has to know how to search for the autocomplete

```

Add validations to fields, [Django Validators](https://docs.djangoproject.com/en/4.1/ref/validators/):

on **models.py**

```python
from django.core.validators import MinValueValidator

[...]
class Product(models.Model):
    #Unit Price with minimum value = 1
    unit_price = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(1, message='Minimum value not reached')]
    )
    #Promotion as Optional (blank=True)
    promotions = models.ManyToManyField(Promotion, blank=True)

```

Editing Child using Inlines:

```python
class OrderItemInline(admin.TabularInline):
    model = models.OrderItem

## ORDERS
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    [...]
```

### Generic relations

in **tags/admin.py**

```python

from .models import Tag

#admin.site.register(Tag)
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	search_fields = ['label'] # Used in case we want to use Autocompletion
```

in **tags/models.py**

```python
class Tag(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.label
```

in **store/admin.py**
Before the first store Model class (ProductAdmin)

```python
from django.contrib.contenttypes.admin import GenericTabularInline
from tags.models import TaggedItem
[...]

class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem # This has to be imported

## PRODUCTS
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    inlines = [TagInline] # Used to  include the Tag as inline for a new Product
    list_display = ['id','title','unit_price','inventory_status', 'collection_title']
    list_editable = ['unit_price']
    ordering = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title__istartswith']
    list_filter = ['collection','last_update', InventoryFilter]

```

### Extending Pluggable Apps

in **store/admin.py** we included

```python
from tags.models import TaggedItem
```
But this is not Idea as we cannot deploy store APP without tags APP

So we are going to create a New APP "store_custom" which knows about both apps

```bash
python manage.py startapp store_custom
```

So

 - We move the **TagInline()** class from **store/admin.py** to **store_custom/admin.py**
 - in **store/admin.py** We remove ```inlines = [TagInline]``` from *ProductAdmin* class
 - in **store_custom/admin.py** We create a **CustomProductAdmin** class
 - in **store_custom/admin.py** We Unregister old product admin manager (*ProductAdmin*) and register to the new one (*CustomProductAdmin*)

in **store_custom/admin.py**

```python
from store.admin import ProductAdmin #Tins has to be imported to refers to the origin Store app
from tags.models import TaggedItem
from django.contrib.contenttypes.admin import GenericTabularInline

class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem # This has to be imported

admin.site.unregister(Product) # Unregister old product admin manager (ProductAdmin)
admin.site.register(Product, CustomProductAdmin) # Register new product admin manager (CustomProductAdmin)

```

and as a last point we include the new app **store_custom** in the *INSTALLED_APPS*
in **storefront/settings.py**

## CACHING

in **settings.py**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
```
```bash
python manage.py createcachetable
```

## QUEUEING (DJANGO Q)

```bash
pip install django-q
```

in **settings.py**

```python
INSTALLED_APPS = [
    ...
    'django_q',
    ...
]
...
Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 4,
    'timeout': 90,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default'
}
```
```bash
python manage.py qcluster
```
/home/gzamataro/Downloads/Django- Resources/Resources/Code/5- Django ORM/Start/storefront/bots