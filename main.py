import uuid
from multiprocessing import queues, Process

import flask
import googleapiclient.discovery
import httplib2
from flask import request
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.client import AccessTokenCredentials

from acces_token import get_auth_code

storage_path = "/data/"

# TODO: "нет места экскпшн"
# TODO: "очередь, отказоустойчиво"
CLIENT_SECRETS_FILE = "client.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtubepartner",
          "https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = flask.Flask(__name__)
app.secret_key = 'test'
queue = queues.Queue()


def upload_video(path, title, description):
    credentials = AccessTokenCredentials(
        access_token=get_auth_code(), user_agent='tests'
    )
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, http=credentials.authorize(httplib2.Http()))

    zapros = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": "22",
                "description": description,
                "title": title
            },
            "status": {
                "privacyStatus": "private"
            }
        },
        media_body=MediaIoBaseUpload(open(path), mimetype="video/mp4", resumable=True)
    )
    otvet = zapros.execute()
    link = f'https://www.youtube.com/watch?v={otvet["id"]}&ab_channel={otvet["snippet"]["channelId"]}'
    print(link)  ## send to database link, name, description


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/upload', methods=["POST"])
def upload():
    video = request.files.get('uploadfile').read()
    id = uuid.uuid4().hex

    with open(storage_path + id, "w") as file:
        file.write(video)

    queue.put({"path": storage_path + id, "title": "name", "description": "desc", "id": id})
    ## Send to DB path, id, name and desc, status "saved"

    return "success"


@app.route('/success')
def success():
    return "uploaded"


@app.route('/form')
def form():
    return app.send_static_file("form.html")


def manage_uploads_to_youtube():
    ## For every file existing in fs on the start:
    ## list_of_files - loaded on the start
    ## если в бд состояние uploaded - удалить
    ## если в бд состояние saved - загрузить из БД параметры и добавить видео в очередь на загрузку queue.put()

    process_dict = {}
    while True:
        for k, v in process_dict.items():
            if v["process"].exitcode == 0:
                ## update status in bd to uploaded
                ## Remove file from filesystem
                process_dict.pop(k)
            if not v['process']._popen:
                v['process'].start()


        if queue.get():
            video = queue.get()
            process_dict[video["id"]] = dict(
                process=Process(target=upload_video, args=(video['path'], video['title'], video['description'])),
                args=video)


if __name__ == "__main__":
    Process(target=app.run).start()
    manage_uploads_to_youtube()
