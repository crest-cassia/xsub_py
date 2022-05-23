# Procedure of integration test

To verify xsub working properly, test the following items.

## testing xsub

- run `xsub -t`
    ```shell
    $ xsub -t
    ```
    - Verify output JSON has "parameters" and "template" keys like the above

- run xsub command as follows. (change the parameters properly for each host.)
    ```shell
    $ xsub sleep5.sh -d work_dir -l log_dir -p '{"mpi_procs":2,"omp_threads":4}'
    ```
    - Verify that JSON is printed to stdout. It should contain "job_id" key.
    - Verify that a job is submitted to the scheduler
    - Verify that `work_dir/sleep5_xsub.sh` is created and it has appropriate parameters
    - Verify that `log_dir/xsub.log` is created and the log is written to this file
    - Verify that `work_dir/pwd.txt` contains the path to work_dir after the job has finished
    - Clean up the temporary directories as follows:
        ```shell
        $ rm -rf work_dir log_dir
        ```

## testing xstat

- Run `xsub` and `xstat` command as follows.
    ```shell
    $ xsub sleep5.sh -d work_dir -l log_dir   # run xsub. JSON like the following will be printed.
    {
      "job_id": "12345"
    }
    $ xstat 12345     # run xstat with the above job_id. JSON like the following will be printed.
    {
      "status": "running",
      "raw_output": [
        "  PID TTY           TIME CMD",
        "12345 ttys001    0:00.00 bash /Users/murase/work/xsub/test/sleep5_xsub2.sh"
      ]
    }
    ```
    - Verify that JSON with the status "queued" or "running" is printed.
    - After the job finished, run `xstat` command again and verify that the status changed to "finished".
        ```shell
        $ xstat 12345
        {
            "status": "finished"
        }
        ```
    - To clean up the temporary directories,
        ```shell
        $ rm -rf work_dir log_dir
        ```

- [ ] Test multiple job submission and status

- Run `xstat` without argument and verify that the status of the job scheduler is displayed in plain text format.
    ```shell
    $ xstat
    ```

## testing xdel

- Run the following command. (Replace the `job id` with yours.)
    ```shell
    $ xsub sleep5.sh -d work_dir -l log_dir   # Run xsub. The job_id will be displayed like the following.
    $ xdel 1234         # Run xdel to cancel the job.
    $ xstat 1234        # Check if the job is really canceled by xstat command.
    ```
    - Verify the job is deleted using the status command of the scheduler
    - To clean up the temporary directories, run
        ```shell
        $ rm -rf work_dir log_dir
        ```
