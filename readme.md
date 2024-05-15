# xsub-py

Another implementation of [xsub](https://github.com/crest-cassia/xsub) in Python.
XSUB is a wrapper for job schedulers. Job schedulers used in HPCs, such as Torque, often have its own I/O format.
Users have to change their scripts to conform with its dialect. This is a wrapper script to absorb the difference.
This script is intended to be used by [OACIS](https://github.com/crest-cassia/oacis).

Although only a few types of schedulers are currently supported, you can extend xsub easily to support other schedulers.
We are also happy to receive your pull requests on your extensions to support more schedulers.

## Installation

- Python 3.6 or later is required.
- Clone this repository

  ```shell
  git clone https://github.com/crest-cassia/xsub_py.git
  ```

- set `PATH` and `XSUB_TYPE` environment variables in your `~/.bash_profile`
  - set `PATH` so as to include the `bin` directory of this repository. Then you can use `xsub`, `xstat`, and `xdel` commands.
  - set `XSUB_TYPE` to be one of the supported schedulers listed below.
  - If you run xsub from OACIS, please set these variables in `.bash_profile` even if your login shell is zsh. This is because OACIS executes `xsub` on bash launched as a login shell.
    - do **NOT** set these environment variables in `.bashrc` because it is loaded only in an interactive shell, not in a login shell.

  ```sh:.bash_profile
  export PATH="$HOME/xsub_py/bin:$PATH"
  export XSUB_TYPE="none"
  ```

### Supported Schedulers

List of available schedulers.

- **none**
  - If you are not using a scheduler, please use this. The command is executed as a usual process.
- **torque**
  - [Torque](http://www.adaptivecomputing.com/products/open-source/torque/)
  - `qsub`, `qstat`, `qdel` commands are used.
- **slurm**
  - [SLURM](https://slurm.schedmd.com/)
  - `sbatch`, `squeue`, `scancel` commands are used.
- **fugaku**
  - Fugaku
  - `pjsub`, `pjstat`, `pjdel` commands are used.

## Contact

- Send your feedback to us!
  - `oacis-dev _at_ googlegroups.com` (replace _at_ with @)
  - We appreciate your questions, feature requests, and bug reports.

## License

The MIT License (MIT)

Copyright (c) 2022 RIKEN, R-CCS

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Specification

The specification is identical to that of [the ruby version of xsub](https://github.com/crest-cassia/xsub#specification).

## Extending

- Fork the repository.
- Add another module in `bin/schedulers` directory. Let's say `your_scheduler.py` is your new module.
  - In your new module, define a new class, say `YourScheduler`, that contains the following constants and static methods.
    - constants: `TEMPLATE`
    - static methods:
      - `validate_parameters(params: dict) -> None`
      - `parent_script(parametes: dict, job_file: pathlib.Path, work_dir: pathlib.Path) -> str`
      - `submit_job(script_path: pathlib.Path, work_dir: pathlib.Path, log_dir: pathlib.Path, log: io.TextIOBase, parameters: dict) -> tuple[str,str]`
      - `all_status() -> str`
      - `multiple_status(job_ids: list[str]) -> dict[str,tuple[str,str]]`
      - `delete(job_id: str) -> str`
  - Examples can be found at [schedulers](https://github.com/yohm/xsub_py/tree/main/bin/schedulers) directory.
- Edit `bin/schedulers/__init__.py`
  - Add your scheduler class to `SCHEDULER_TYPES` like the following.
    ```diff
    SCHEDULER_TYPES = {
    -  "none": none.NoneScheduler
    +  "none": none.NoneScheduler,
    +  "your_scheduler": your_scheduler.YourScheduler
    }
    ```
- After you implemented your scheduler class, test following the instructions [here](test/instruction.md).
- set `XSUB_TYPE` environment variable to your new module name.
  - add `XSUB_TYPE=your_scheduler` to your `.bash_profile`. (case-insensitive)
- We would appreciate it if you send us your enhancement as a pull request:grin:

### Sending a pull request

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
