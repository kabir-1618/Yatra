# import requests

# INSTAMOJO_API_ENDPOINT = 'https://api.instamojo.com/v2/'
# INSTAMOJO_AUTH_ENDPOINT = 'https://www.instamojo.com/oauth2/token/'

# def generate_instamojo_access_token(api_key, api_secret):
#     response = requests.post(INSTAMOJO_AUTH_ENDPOINT, data={
#         'client_id': api_key,
#         'client_secret': api_secret,
#         'grant_type': 'client_credentials'
#     })

#     if response.status_code == 200:
#         return response.json()['access_token']
#     else:
#         return None

# def create_instamojo_payment_request(amount, purpose, buyer_name, buyer_email, redirect_url):
#     api_key="e0c97f7f54762e076c7ee1afe2e0378c"
#     api_secret="ad6732bc405d45c2a706a764d9e56feb"
#     access_token = generate_instamojo_access_token(api_key, api_secret)

#     if access_token is None:
#         print("Hello")
#         return None

#     response = requests.post(INSTAMOJO_API_ENDPOINT + 'payment_requests/', headers={
#         'Authorization': 'Bearer ' + access_token
#     }, data={
#         'amount': amount,
#         'purpose': purpose,
#         'buyer_name': buyer_name,
#         'buyer_email': buyer_email,
#         'redirect_url': redirect_url
#     })

#     if response.status_code == 201:
#         return response.json()['payment_request']['longurl']
#     else:
#         return None

from instamojo_wrapper import Instamojo
api = Instamojo(api_key="c1c69c95d0907ab6d3f4765721d47a72",
                    auth_token="fda7f9ab4e5bda554814a6ae3a176ff4")
def payment_request(email, amount, purpose):
    

    # Create a new Payment Request
    response = api.payment_request_create(
        amount=amount,
        purpose=purpose,
        send_email=True,
        email=email,
        redirect_url="http://localhost:8000/payment"
        )
    # print the long URL of the payment request.
    # print(response['payment_request']['longurl'])
    print(response)
    # print the unique ID(or payment request ID)
    # print(response['payment_request']['id'])
    print(response['payment_request']['longurl'])
    return response['payment_request']['longurl']

def payment_details(payment_request_id, payment_id):
    response = api.payment_request_payment_status(payment_request_id,payment_id)
    return response
