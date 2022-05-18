import pathlib,io,os,subprocess

class NoneScheduler:

  TEMPLATE = '''\
. {_job_file}
'''

  PARAMETERS = {
    "mpi_procs":   { "description": "MPI process", "default": 1, "format": r'^[1-9]\d*$'},
    "omp_threads": { "description": "OMP threads", "default": 1, "format": r'^[1-9]\d*$'}
  }

  @staticmethod
  def validate_parameters(params: dict):
    # check if the given parameters are valid
    # if not valid, raise an Exception
    pass

  @staticmethod
  def submit_job(script_path: pathlib.Path, work_dir: pathlib.Path, log_dir: pathlib.Path, log: io.TextIOBase, parameters: dict):
    cmd = f"nohup bash {script_path.absolute()} > /dev/null 2>&1 < /dev/null & echo $!"
    print(cmd)
    log.write(f"{cmd} is invoked\n")
    output = ""
    os.makedirs(work_dir, exist_ok=True)
    result = subprocess.run(cmd, shell=True, cwd=work_dir, check=True, capture_output=True)
    print(result)
    psid = str(int(result.stdout.splitlines()[-1]))
    log.write(f"process id: {psid}\n")
    return {"job_id": psid, "raw_output": [line.decode().rstrip() for line in result.stdout.splitlines()]}
