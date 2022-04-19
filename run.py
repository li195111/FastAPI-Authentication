import uvicorn

from main import app

original_callback = uvicorn.main.callback


def callback(**kwargs):
  from celery.contrib.testing.worker import start_worker

  import tasks

  with start_worker(tasks.task, perform_ping_check=False, loglevel="info"):
    original_callback(**kwargs)


uvicorn.main.callback = callback

if __name__ == "__main__":
  import os
  import sys
  import threading
  import multiprocessing
  # Execute redis-server
  redis = threading.Thread(target=os.system, args=('redis-server', ))
  redis.start()

  celery_schedule = multiprocessing.Process(target=os.system,
                                            args=('celery -A tasks beat', ))
  celery_schedule.start()

  frontend = multiprocessing.Process(
      target=os.system, args=('cd auth-front-end && npm run dev', ))
  frontend.start()

  # uvicorn filename:app
  sys.argv += ['main_oauth2:app', '--reload', '--host=0.0.0.0', '--port=3000']
  uvicorn.main()

  redis.join()
  celery_schedule.join()
  frontend.join()
