import requests

# ValueError should rise
# data = requests.post('http://127.0.0.1:5000/message/',
#                       json={
#                           'title': 'third_message',
#                           'owner_name': 'user_2user_2user_2user_2user_2user_2'
#                       })

# POST
# data = requests.post('http://127.0.0.1:5000/message/',
#                       json={
#                           'title': 'third_message',
#                           'owner_name': 'user_2'
#                       })

# PATCH
# data = requests.patch('http://127.0.0.1:5000/message/1',
#                       json={
#                           'title': 'bla_bla_bla!!!'
#                       })

# DELETE
# data = requests.delete('http://127.0.0.1:5000/message/1')


# GET
# data = requests.get('http://127.0.0.1:5000/message/1')

# POST
# data = requests.post('http://127.0.0.1:5000/message/',
#                       json={
#                           'title': 'hello world',
#                           'text': 'just wanted to say hi...!!!',
#                           'owner_name': 'some_user'
#                       })

# print(data.status_code)
# print(data.text)
