import requests
import json

response = requests.get('http://127.0.0.1:5000/products')
params={'limit': 5, offset: 0}
print(json.loads(response.content))

response = requests.get('http://127.0.0.1:5000/customers')
print(json.loads(response.content))

response = requests.get('http://127.0.0.1:5000/carts')
print(json.loads(response.content))

response = requests.post('http://127.0.0.1:5000/products/add',
                         json={'name': "AirPods 2", 'description': "Безпроводные наушники", 'price': 10500})
json={'name': 'AirPods 2', 'description': '', 'price': 10500}
print(json.loads(response.content))

response = requests.post('http://127.0.0.1:5000/customers/add',
                         json={'name': "Vasia", 'phone': "89175361223", 'email': "vasia@gmail.com"})

response = requests.post('http://127.0.0.1:5000/carts/add',
                         json={'customer_id': 2, 'product_id': 5})