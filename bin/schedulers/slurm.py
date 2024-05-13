import pathlib,io,subprocess,datetime,re
from typing import List,Tuple,Dict

class SlurmScheduler:

  PARAMETERS = {
    "mpi_procs": { "description": "MPI process", "default": 1, "format": r'^[1-9]\d*$'},
    "omp_threads": { "description": "OMP threads", "default": 1, "format": r'^[1-9]\d*$'},
    "ppn": { "description": "Process per nodes", "default": 1, "format": r'^[1-9]\d*$'},
    "walltime": { "description": "Limit on elapsed time", "default": "24:00:00", "format": r'^\d+:\d{2}:\d{2}$'}
  }

  @staticmethod
  def validate_parameters(params: dict) -> None:
    mpi = int(params["mpi_procs"])
    omp = int(params["omp_threads"])
    ppn = int(params["ppn"])
    if mpi <= 0 or omp <= 0 or ppn <= 0:
      raise Exception("mpi_procs, omp_threads, and ppn must be larger than 1")
    if (mpi*omp)%ppn != 0:
      raise Exception("(mpi_procs * omp_threads) must be a multiple of ppn")

  @staticmethod
  def parent_script(parameters: dict, job_file: pathlib.Path, work_dir: pathlib.Path) -> str:
    template = '''\
#!/bin/bash -x
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={ppn}
#SBATCH --time={walltime}
. {job_file}
'''
    ppn = int(parameters['ppn'])
    nodes = int(int(parameters['mpi_procs'])*int(parameters['omp_threads'])/ppn)
    walltime = parameters['walltime']
    return template.format(nodes=nodes, ppn=ppn, walltime=walltime, job_file=job_file)

  @staticmethod
  def submit_job(script_path: pathlib.Path, work_dir: pathlib.Path, log_dir: pathlib.Path, log: io.TextIOBase, parameters: dict) -> Tuple[str,str]:
    cmd = f"sbatch -D {work_dir.absolute()} -o {log_dir.absolute()}/xsub.log -e {log_dir.absolute()}/xsub.log {script_path.absolute()}"
    log.write(f"cmd: {cmd}\ntime: {datetime.datetime.now()}")
    result = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE)
    output = result.stdout.decode()
    if result.returncode != 0:
      log.write(f"rc is not zero: {result.returncode} {output}")
      raise Exception(f"rc is not zero: {output}")
    job_id = output.splitlines()[-1].split(" ")[-1]
    log.write(f"job_id: {job_id}")
    return (job_id, output)

  @staticmethod
  def all_status() -> str:
    cmd = "squeue"
    result = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE)
    return result.stdout.decode()

  @staticmethod
  def multiple_status(job_ids: List[str]) -> Dict[str,Tuple[str,str]]:
    cmd = "squeue"
    result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)
    output_list = result.stdout.decode().splitlines()

    results = {}
    for job_id in job_ids:
      pattern = re.compile(f"^\\s*{job_id}")
      matched = [line for line in output_list if pattern.match(line)]
      if matched:
        results[job_id] = SlurmScheduler._parse_status(matched[-1])
      else:
        results[job_id] = ("finished", "not found in squeue")
    return results

  @staticmethod
  def _parse_status(line: str) -> Tuple[str,str]:
    c = line.split()[4]
    if c == 'PD':
      return ("queued", line)
    elif c == 'R' or c == 'T' or c == 'E':
      return ("running", line)
    elif c == 'C':
      return ("finished", line)
    else:
      raise Exception(f"unknown format {str}")

  @staticmethod
  def delete(job_id: str) -> str:
    cmd = f"scancel {job_id}"
    result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)
    return result.stdout.decode()
