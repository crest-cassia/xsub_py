from . import none


def create(scheduler_name):
  if scheduler_name == "none":
    return none.NoneScheduler;
