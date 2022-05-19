import os,sys
from . import none


SCHEDULER_TYPES = {
  "none": none.NoneScheduler
}

def create():
  if not 'XSUB_TYPE' in os.environ:
    print(f"[Error] Set environment variable 'XSUB_TYPE'")
    print(f"        available values are {','.join(SCHEDULER_TYPES.keys())}")
    raise Exception(f"environment variable 'XSUB_TYPE' is not set")
  xsub_type = os.environ['XSUB_TYPE'].lower()
  if not xsub_type in SCHEDULER_TYPES:
    print(f"[Error] invalid scheduler type {xsub_type}", file=sys.stderr)
    raise Exception(f"scheduler type {xsub_type} is not found")
  return SCHEDULER_TYPES[xsub_type]
