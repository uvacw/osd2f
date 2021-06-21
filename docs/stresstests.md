# Running a stress test

## Requiments

- `osd2f` is installed
- `requirments_dev.txt` dependencies are installed

## In short

Stresstest help you pinpoint the amount of traffic your server is able to
handle. OSD2F provides a script for the popular Python load-test library 
[locust](https://locust.io/). 

The files submitted are generated using the mock data generating scripts. 

## How to run a stress test

To run a stresstest, you require a running instance of OSD2F, either locally 
or on a reachable address. You can run the script from CLI (no interface)
using:

```bash
locust \
    --host http://localhost:5000 \
    -f scripts/locust_stress_test.py \
    --headless \
    --users 100 \
    -t 60sec
```

where:
- `host` is the location of the server you want to stresstest
- `-f` points to the stress test file
- `headless` means no locust web interface is started
- `users` is the amount of concurrent users simulated. The script 
  assumes each user will send 20 logs for each 1 call to anonymization
  and 1 call to submissions. For details, review the stresstest script.

## important notes

- The data-sizes and ratio of logs/anomymization/submission calls should
  be based on empirical observations in your sample. Current numbers may 
  not reflect those for your population or use-case. 