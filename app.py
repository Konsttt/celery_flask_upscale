import os

from flask import Flask, send_file, render_template
from flask import request
from flask.views import MethodView
from flask import jsonify
from celery import Celery
from celery.result import AsyncResult
from PIL import Image
import io
import base64

from upscale import upscale


app_name = 'app'
app = Flask(app_name)
# app.config['UPLOAD_FOLDER'] = 'upscale_image'
celery = Celery(
    app_name,
    backend='redis://localhost:6379/1',
    broker='redis://localhost:6379/2'
)
celery.conf.update(app.config)


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask


@celery.task()
def upscale_image(path_1, path_2):
    result = upscale(path_1, path_2)
    return result




class UpscaleMethod(MethodView):

    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        return jsonify({'status': task.status,
                        'result': task.result})

    def post(self):
        image_paths = self.upscale_image_path()
        print(*image_paths)
        task = upscale_image.delay(*image_paths)
        return jsonify(
            {'task_id': task.id}
        )

    def upscale_image_path(self):
        json_data = request.json
        original_name = json_data['image']
        upscale_name_, extension = original_name.split('.')
        upscale_name = f'{upscale_name_}_upscale.{extension}'
        current_path = os.getcwd()
        path1 = os.path.join(current_path, 'origin_image', original_name)
        path2 = os.path.join(current_path, 'upscale_image', upscale_name)
        return [path1, path2]


class GetFileMethod(MethodView):

    def get(self, filename):
        current_path = os.getcwd()
        path_ = os.path.join(current_path, 'upscale_image', filename)
        im = Image.open(path_)
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())
        return render_template("image.html", img_data=encoded_img_data.decode('utf-8'))

        # # Этот код для скачивания файла
        # current_path = os.getcwd()
        # path_ = os.path.join(current_path, 'upscale_image', filename)
        # return send_file(path_, as_attachment=True)

upscale_view = UpscaleMethod.as_view('upscale')
app.add_url_rule('/upscale/', view_func=upscale_view, methods=['POST'])
app.add_url_rule('/tasks/<string:task_id>', view_func=upscale_view, methods=['GET'])
processed_view = GetFileMethod.as_view('processed')
app.add_url_rule(f'/processed/<filename>', view_func=processed_view, methods=['GET'])


if __name__ == '__main__':
    app.run()
