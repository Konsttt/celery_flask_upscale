import requests
import base64
import time

# Здесь может быть любой файл из папки origin_image
file_name = "111.png"

response = requests.post('http://127.0.0.1:5000/upscale/', json={"image": file_name})

response_data = response.json()
task_id = response_data['task_id']
print(task_id)
status = 'PENDING'
result = None

while status == 'PENDING':
    response = requests.get(f'http://127.0.0.1:5000/tasks/{task_id}')
    response_json = response.json()
    print(response_json)
    status = response_json['status']
    result = response_json['result']
    time.sleep(3)

print(status)
print(result)

upscale_name_, extension = file_name.split('.')
upscale_name = f'{upscale_name_}_upscale.{extension}'
print()
print('Открыть обработанный файл в браузере:')
print(f'http://127.0.0.1:5000/processed/{upscale_name}')

