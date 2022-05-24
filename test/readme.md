# Procedure of integration test

To verify that xsub, xstat, xdel are working properly, test the following items.

## testing xsub

- run `xsub -t`
    ```shell
    $ xsub -t
    ```
    - Verify output JSON has "parameters" and "template" keys like the following:
        ```json
        {
          "parameters": {
            "mpi_procs": {
              "description": "MPI process",
              "default": 1,
              "format": "^[1-9]\\d*$"
            },
            "omp_threads": {
              "description": "OMP threads",
              "default": 1,
              "format": "^[1-9]\\d*$"
            }
          },
          "template": [
            ". {_job_file}"
          ]
        }
        ```

- run xsub command as follows. (change the parameters properly for each host.)
    ```shell
    $ xsub sleep10.sh -d work_dir -l log_dir -p '{"mpi_procs":2,"omp_threads":4}'
    ```
    - Verify that JSON is printed to stdout. It should contain "job_id" key like the following:
        ```json
        {
          "job_id": "41988",
          "raw_output": [
            "41988"
          ],
          "parent_script": "/path/to/xsub_py/work_dir/sleep10_xsub1.sh"
        }
        ```
    - Verify that the job is submitted to the scheduler.
    - Verify that `work_dir/sleep10_xsub.sh` is created with the specified parameters.
    - Verify that `log_dir/xsub.log` is created and the log is appended to this file.
    - Verify that `work_dir/pwd.txt` contains the path to work_dir after the job has finished.
    - Clean up the temporary directories as follows:
        ```shell
        $ rm -rf work_dir log_dir
        ```

## testing xstat

- First, run `xsub` as follows.
    ```shell
    $ xsub sleep10.sh -d work_dir -l log_dir
    ```
    - JSON like the following will be printed.
        ```json
        {
          "job_id": "12345",
          ...
        }
        ```
- Run `xstat -m <JOB_ID>` with the job ID shown by `xsub`. You must do it while the job is running, namely, within 10 seconds. If you couldn't make it, run `xsub` again.
    ```shell
    $ xstat -m 12345
    ```
    - You will see the output like the following. Make sure that the status is `running`:
        ```json
        {
          "12345": {
            "status": "running",
            ...
          }
        }
        ```
    - Verify that JSON with the status "queued" or "running" is printed.
- After the job finished, run `xstat` command again and verify that the status changed to "finished".
    ```shell
    $ xstat -m 12345
    ```
    - Output will be like the following. Make sure that the status became `finished`:
        ```json
        {
          "12345": {
            "status": "finished",
            ...
          }
        }
        ```
- Clean up the temporary directories after you completed the tests.
    ```shell
    $ rm -rf work_dir log_dir
    ```

- Run `xstat` without argument and verify that the status of the job scheduler is displayed in plain text format.
    ```shell
    $ xstat
    ```
    - Output will be like the following. An output of the scheudler will be shown:
        ```text
        USER     PID  %CPU %MEM      VSZ    RSS   TT  STAT STARTED     TIME COMMAND
        foobar 74357  19.3  0.6  6602472 201140   ??  S    土02PM   4:29.57 /Applications/...
        ...
        ```

## testing xdel

- Run the following command. (Replace the `job id` with yours.)
    ```shell
    $ xsub sleep10.sh -d work_dir -l log_dir
    ```
- While your job is running, run `xdel` to cancel the job like the following:
    ```shell
    $ xdel 12345
    ```
- Verify that the job is properly terminated by running `xstat` command.
    ```shell
    $ xstat 12345
    ```
    - The status of the job should be 'finished'.
- Clean up the temporary directories by the following command:
    ```shell
    $ rm -rf work_dir log_dir
    ```
