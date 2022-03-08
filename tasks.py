from celery import Celery

task = Celery('tasks',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

'''
@task.task
def function():
    ... 
'''