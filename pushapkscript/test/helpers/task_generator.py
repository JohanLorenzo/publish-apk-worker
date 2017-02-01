import os
import json


class TaskGenerator(object):
    def __init__(self, apks=None):
        self.apks = apks if apks is not None else {
            'armv7_v15': 'https://queue.taskcluster.net/v1/task/WNIh4L_BTVKZhDk0KUAptQ/artifacts/\
public/build/fennec-52.0a2.multi.android-arm.apk',
            'x86': 'https://queue.taskcluster.net/v1/task/WFVQok4TQOmUS8F6p2VFDw/artifacts/\
public/build/fennec-52.0a2.multi.android-i386.apk'
        }

    def generate_file(self, work_dir):
        task_file = os.path.join(work_dir, 'task.json')
        with open(task_file, 'w') as f:
            json.dump(self.generate_json(), f)
        return task_file

    def generate_json(self):
        return json.loads('''{{
          "provisionerId": "some-provisioner-id",
          "workerType": "some-worker-type",
          "schedulerId": "some-scheduler-id",
          "taskGroupId": "some-task-group-id",
          "routes": [],
          "retries": 5,
          "created": "2015-05-08T16:15:58.903Z",
          "deadline": "2015-05-08T18:15:59.010Z",
          "expires": "2016-05-08T18:15:59.010Z",
          "dependencies": ["WFVQok4TQOmUS8F6p2VFDw", "WNIh4L_BTVKZhDk0KUAptQ"],
          "scopes": ["project:releng:googleplay:aurora"],
          "payload": {{
            "apks": {apks},
            "google_play_track": "alpha"
          }}
        }}'''.format(apks=json.dumps(self.apks)))
