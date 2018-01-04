import os
import json


class TaskGenerator(object):
    def __init__(self, google_play_track='alpha', rollout_percentage=None, google_play_strings_task=True):
        self.arm_task_id = 'fwk3elTDSe6FLoqg14piWg'
        self.x86_task_id = 'PKP2v4y0RdqOuLCqhevD2A'
        self.google_play_strings_task = google_play_strings_task
        if self.google_play_strings_task is True:
            self.google_play_strings_task_id = 'bgP9T6AnTpyTVsNA7M3OnA'
        self.google_play_track = google_play_track
        self.rollout_percentage = rollout_percentage

    def generate_file(self, work_dir):
        task_file = os.path.join(work_dir, 'task.json')
        with open(task_file, 'w') as f:
            json.dump(self.generate_json(), f)
        return task_file

    def generate_json(self):
        json_content = json.loads('''{{
          "provisionerId": "some-provisioner-id",
          "workerType": "some-worker-type",
          "schedulerId": "some-scheduler-id",
          "taskGroupId": "some-task-group-id",
          "routes": [],
          "retries": 5,
          "created": "2015-05-08T16:15:58.903Z",
          "deadline": "2015-05-08T18:15:59.010Z",
          "expires": "2016-05-08T18:15:59.010Z",
          "dependencies": ["{arm_task_id}", "{x86_task_id}"],
          "scopes": ["project:releng:googleplay:aurora"],
          "payload": {{
            "upstreamArtifacts": [{{
              "paths": ["public/build/target.apk"],
              "taskId": "{arm_task_id}",
              "taskType": "signing"
            }}, {{
              "paths": ["public/build/target.apk"],
              "taskId": "{x86_task_id}",
              "taskType": "signing"
            }}],
            "google_play_track": "{google_play_track}"
          }}
        }}'''.format(
            arm_task_id=self.arm_task_id,
            x86_task_id=self.x86_task_id,
            google_play_track=self.google_play_track,
        ))

        if self.rollout_percentage:
            json_content['payload']['rollout_percentage'] = self.rollout_percentage

        if self.google_play_strings_task:
            json_content['payload']['upstreamArtifacts'].append({
               'paths': ['public/google_play_strings.json'],
               'taskId': self.google_play_strings_task_id,
               'taskType': 'fetch',
               'optional': True,
             })

        return json_content
