# import json
# import requests

# try:
#     response = requests.get(
#         "https//example.com",
#         timeout=5
#     )

#     response.raise_for_status()
#     print(response.json())
# except requests.exceptions.RequestException as e:
#     print("APi Error", e)

def check_stock(stock, quantity):
    if stock >= quantity:
        print("Stock Available")
    else:
        print("Insufficient Stock")
check_stock(quantity=1, stock=1)