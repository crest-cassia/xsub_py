import pathlib,io,subprocess,re,functools
from typing import List,Tuple,Dict

class FugakuScheduler:

  PARAMETERS = {
    'mpi_procs': { "description": 'MPI process', "default": 1, "format": r'^[1-9]\d*$' },
    'max_mpi_procs_per_node': { "description": 'Max MPI processes per node', "default": 1, "format": r'^[1-9]\d*$' },
    'omp_threads': { "description": 'OMP threads', "default": 1, "format": r'^[1-9]\d*$' },
    'elapse': { "description": 'Limit on elapsed time', "default": '1:00:00', "format": r'^\d+:\d{2}:\d{2}$' },
    'node': { "description": 'Nodes', "default": '1', "format": r'^\d+(x\d+){0,2}$' },
    'shape': { "description": 'Shape', "default": '1', "format": r'^\d+(x\d+){0,2}$' },
    'low_priority_job': { "description": 'Low priority job(s)?', "default": 'false', "format": r'^(true|false)$' }
  }

  @staticmethod
  def validate_parameters(params: dict) -> None:
    num_procs = int(params['mpi_procs'])
    num_threads = int(params['omp_threads'])
    if num_procs < 1 or num_threads < 1:
      raise Exception('mpi_procs and omp_threads must be larger than or equal to 1')

    node_values = [int(n) for n in params['node'].split('x')]
    shape_values = [int(n) for n in params['shape'].split('x')]
    if len(node_values) != len(shape_values):
      raise Exception('node and shape must be a same format like node=>4x3, shape=>1x1')
    if any([n < s for (n,s) in zip(node_values,shape_values)]):
      raise Exception('each # in node cannot be smaller than the one in shape')

    max_num_procs_per_node = int(params['max_mpi_procs_per_node'])
    if max_num_procs_per_node * num_threads > 48:
      raise Exception('max_mpi_procs_per_node times omp_threads must be less than or equal to 48')

    shape_total = functools.reduce(lambda x,y: x*y, shape_values)
    max_num_procs = shape_total * max_num_procs_per_node
    if num_procs > max_num_procs:
      raise Exception("mpi_procs must be less than or equal to #{max_num_procs}")

    low_priority_job = params['low_priority_job']
    if low_priority_job != 'true' and low_priority_job != 'false':
      raise Exception('low_priority_job must be "true" or "false"')

  @staticmethod
  def _rscgrpname(node, elapse, low_priority_job):
    num_nodes = functools.reduce(lambda x,y: x*y, [int(x) for x in node.split("x")])
    elapse_time_sec = functools.reduce(lambda x,y: x*60+y, [int (x) for x in elapse.split(':')])
    is_low_priority_job = True if low_priority_job == 'true' else False

    if is_low_priority_job:
      if num_nodes <= 384 and elapse_time_sec <= 43200: # <= 12h
        return 'small-free'
      elif num_nodes <= 55296 and elapse_time_sec <= 43200: # <= 12h
        return 'large-free'
      else
        return ''
    else:
      if num_nodes <= 384 and elapse_time_sec <= 259200: # <= 72h
        return 'small'
      elif num_nodes <= 55296 and elapse_time_sec <= 86400: # <= 24h
        return 'large'
      else:
        return ''

  @staticmethod
  def parent_script(parameters: dict, job_file: pathlib.Path, work_dir: pathlib.Path) -> str:
    template = '''\
#!/bin/bash -x
#
#PJM --rsc-list "node={node}"
#PJM --rsc-list "rscgrp={rscgrpname}"
#PJM --rsc-list "elapse={elapse}"
#PJM --mpi "shape={shape}"
#PJM --mpi "proc={mpi_procs}"
#PJM --mpi "max-proc-per-node={mpi_max_proc_per_node}"
#PJM -s
. {_job_file}
'''
    rscgrpname = FugakuScheduler._rscgrpname(parameters['node'], parameters['elapse'], parameters['low_priority_job'])
    return template.format(
      node=parameters['node'], rscgrpname=rscgrpname, elapse=parameters['elapse'],
      shape=parameters['shape'], proc=parameters['mpi_procs'],
      mpi_max_proc_per_node=parameters['mpi_max_proc_per_node'],
      job_file = job_file
    )

  @staticmethod
  def submit_job(script_path: pathlib.Path, work_dir: pathlib.Path, log_dir: pathlib.Path, log: io.TextIOBase, parameters: dict) -> Tuple[str,str]:
    stdout_path = log_dir.joinpath('%j.o.txt')
    stderr_path = log_dir.joinpath('%j.e.txt')
    job_stat_path = log_dir.joinpath('%j.i.txt')

    command = f"cd {work_dir.absolute()} && pjsub {script_path.absolute()} -o {stdout_path.absolute()} -e {stderr_path.absolute()} --spath {job_stat_path.absolute()} < /dev/null"
    log.write(f"cmd: {command}\n")

    result = subprocess.run(command, shell=True, check=False, stdout=subprocess.PIPE)
    output = result.stdout.decode()
    if result.returncode != 0:
      log.write(f"rc is not zero for {command}: {result.returncode}\n")
      log.write(output)
      raise Exception(f"rc is not zero for {command}")

    pattern = re.compile(r"Job (\d+) submitted")
    matched = pattern.search(output)
    if not matched:
      log.write(f"failed to get job_id:\n{output}\n")
      raise Exception(f"failed to get job_id:\n{output}\n")
    job_id = matched.group(1)

    log.write(f"job_id: {job_id}\n")
    return (job_id, output)

  @staticmethod
  def all_status() -> str:
    cmd = 'pjstat --with-summary'
    result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)
    return result.stdout.decode()

  @staticmethod
  def multiple_status(job_ids: List[str]) -> Dict[str,Tuple[str,str]]:
    result = subprocess.run("pjstat", shell=True, check=True, stdout=subprocess.PIPE)
    output_list = result.stdout.decode().splitlines()

    ret = {}
    for job_id in job_ids:
      pattern = re.compile(r'^\s*' + job_id)
      matched = [line for line in output_list if pattern.match(line)]
      if matched:
        ret[job_id] = FugakuScheduler._parse_status(matched[-1])
      else:
        ret[job_id] = ("finished", "not found in pjstat")
    return ret

  @staticmethod
  def _parse_status(line: str) -> Tuple[str,str]:
    c = line.split()[3]

    pq = re.compile(r'ACC|QUE')
    pr = re.compile(r'RNA|RNP|RUN|RNE|RNO|SWO|SWD|SWI|HLD')
    pf = re.compile(r'EXT|RJT|CCL')
    if pq.match(c):
      status = 'queued'
    elif pr.match(c):
      status = 'running'
    elif pf.match(c):
      status = 'finished'
    else:
      status = 'finished'
    return (status, line)

  @staticmethod
  def delete(job_id: str) -> str:
    cmd = f"pjdel {job_id}"
    result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)
    return result.stdout.decode()
