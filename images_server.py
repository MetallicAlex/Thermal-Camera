import os
from flask import send_from_directory, Flask

app = Flask(__name__)


@app.route('/')
def index():
    print('hello')
    return ""


@app.route('/static/images/<filename>', methods=['GET'])
def send_recipe_image_static(filename: str):
    print('hello')
    dirname = os.path.join(os.getcwd(), 'static/images')
    # return ""
    return send_from_directory(dirname, filename)


if __name__ == "__main__":
    app.run(debug=True, host='192.168.1.2', port=7777)
    #app.run(debug=True, host='localhost', port=7777)