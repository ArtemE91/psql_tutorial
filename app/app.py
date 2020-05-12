from flask import Flask, request
from contextlib import closing
import psycopg2
import json

dbname = 'mydb'
host = 'localhost'


def forming_pagination():
    if not request.args.get('offset') and not request.args.get('limit'):
        return 'limit all offset 0'
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    return f'limit {limit} offset {offset}'


def dict_cursor(cursor):
    value = [dict((cursor.description[i][0], value)
                  for i, value in enumerate(row)) for row in cursor.fetchall()]
    return value


def query_db_get(query: str):
    pagination = forming_pagination()
    select = f'{query} {pagination};'
    with closing(psycopg2.connect(database=dbname, host=host)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(select)
            data = dict_cursor(cursor)
    return json.dumps(data)


def query_db_post(query: str, data: tuple):
    with closing(psycopg2.connect(database=dbname, host=host)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, data)
            conn.commit()
            return cursor.fetchone()[0]


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return {}, 200


@app.route('/products/', methods=['GET'])
def get_product():
    # Список продуктов (параметры offset, limit=10)
    # Возращается id, имя товара, цена, фото
    select = 'select p.id, p.name, p.price, pp.url  from product as p'
    join = 'left join product_photo as pp on pp.product_id=p.id'
    order = 'order by p.id'
    query = f'{select} {join} {order}'
    data = query_db_get(query)
    return data, 200


@app.route('/products/add', methods=['POST'])
def post_product():
    data = (request.json["name"], request.json["description"], request.json["price"],)
    insert = 'insert into product (name, description, price) values (%s, %s, %s) RETURNING id;'
    product_id = query_db_post(insert, data)
    return {'id': product_id}, 201


@app.route('/customers/', methods=['GET'])
def get_customer():
    # Список пользователей (параметры offset, limit=10)
    # Возращаем имя, телефон, email
    select = 'select name, phone, email from customer'
    order = 'order by name'
    query = f'{select} {order}'
    data = query_db_get(query)
    return data, 200


@app.route('/customers/add', methods=['POST'])
def post_customer():
    data = (request.json["name"], request.json["phone"], request.json["email"], )
    insert = 'insert into customer (name, phone, email) values (%s, %s, %s) RETURNING id;'
    customer_id = query_db_post(insert, data)
    return {'id': customer_id}, 201


@app.route('/carts/', methods=['GET'])
def get_cart():
    # Список заказов (параметры offset, limit=10)
    # Возращаем отсортированный список по цене
    # имя пользователя, название товара, цена
    select = 'select c.name as customer_name, p.name as product_name, coalesce(p.price, 0) as price from customer as c'
    join_cart = 'left join cart on cart.customer_id=c.id'
    join_cart_product = 'left join cart_product as cp on cp.cart_id=cart.id'
    join_product = 'left join product as p on p.id=cp.product_id'
    where = 'where p.price>0'
    order = 'order by p.price desc'
    query = f'{select} {join_cart} {join_cart_product} {join_product} {where} {order}'
    data = query_db_get(query)
    return data, 200


@app.route('/carts/add', methods=['POST'])
def post_cart():
    data_cart = (request.json['customer_id'], )
    insert_cart = 'insert into cart (customer_id) values (%s) RETURNING id;'
    cart_id = query_db_post(insert_cart, data_cart)
    data_cp = (cart_id, request.json['product_id'], )
    insert_cp = 'insert into cart_product (cart_id, product_id) values (%s, %s) RETURNING cart_id;'
    query_db_post(insert_cp, data_cp)
    return {'cart_id': cart_id}, 201


if __name__ == '__main__':
    app.run(debug=True)


