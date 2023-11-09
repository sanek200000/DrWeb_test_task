from tempfile import NamedTemporaryFile
from flask import Flask, request, send_file, render_template, jsonify
import os
import hashlib

app = Flask(__name__)

# Хранение
UPLOAD_FOLDER = "store"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Хэш
def generate_file_hash(file):
    sha256 = hashlib.sha256()
    with open(file, "rb") as f:
        while True:
            data = f.read(65536)  # Чтение блоками
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/uploadhtml")
def upload():
    return render_template("upload.html")


@app.route("/downloadhtml")
def download():
    return render_template("download.html")


@app.route("/deletehtml")
def delete():
    return render_template("delete.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    # Проверка авторизации пользователя (Basic auth)
    auth = request.authorization
    if not auth or not (
        auth.username == "your_username" and auth.password == "your_password"
    ):
        return "Unauthorized", 401

    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    if file:
        # Вычислить хэш файла
        with NamedTemporaryFile(delete=False) as temp_file:
            print(f"{temp_file.name = }")
            file.save(temp_file.name)
            file_hash = generate_file_hash(temp_file.name)

        # Создать подкаталог
        subfolder = os.path.join(app.config["UPLOAD_FOLDER"], file_hash[:2])
        os.makedirs(subfolder, exist_ok=True)

        # Сохранить файл с именем хэша
        file.seek(0)
        file.save(os.path.join(subfolder, file_hash))
        data = {"path": subfolder, "hash": file_hash}
        # return file_hash, 201
        return jsonify(data)
    else:
        return "File upload failed", 400


@app.route("/download/<file_hash>", methods=["GET"])
def download_file(file_hash):
    # Путь к файлу
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_hash[:2], file_hash)

    if os.path.isfile(file_path):
        return send_file(file_path)
    else:
        return "File not found", 404


@app.route("/delete/<file_hash>", methods=["DELETE"])
def delete_file(file_hash):
    # Проверка авторизации пользователя (Basic auth)
    auth = request.authorization
    if not auth or not (
        auth.username == "your_username" and auth.password == "your_password"
    ):
        return "Unauthorized", 401

    # Путь к файлу
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_hash[:2], file_hash)

    if os.path.isfile(file_path):
        os.remove(file_path)
        return "File deleted", 200
    else:
        return "File not found", 404


if __name__ == "__main__":
    app.run(debug=True)
