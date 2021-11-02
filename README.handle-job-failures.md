# How to Simulate Eden in Production, but Locally

We have multiple eden instances in production.

To simulate this, I prepared a `docker-compose` file that starts locally the folowing containers:

- 3 x `instances of eden` running server_for_docker.py (a counting job)
- `1 nginix` that works as a load balancer for the 3 instances
- `flower` to see what is happening in celery
- `prometheus` to see the metrics exposed by eden
- `redis` to serve the edens

Build eden and start the :point_up: stack:

```bash
docker compose up --build
```

The window where you run `docker-compose` will show logs from all containers. `Ctrl-C` will stop all. If you don't change code, don't rebuild (without `--build`) and will go faster

Of course you can interate by runing edens locally and just point at the redis container. But you're going to miss the load balancer part.

The exposed ports:

Eden "load balancer" is behind port `8080`, it will route requests to to `eden-1`, `eden-2`, `eden-3` containers. They individually are behind `5001`, `5002`, `5003`. You can reach them separately, or via the "load balancer"

To run a job, issue :

```bash
curl http://localhost:8080/run -X POST -H "Content-Type: application/json" -d "{}"
{"token":"uze0zznw78"}%
```

One of the edens will pick it up and you will see in the logs (job just counts to 6 in 10s intervals)

```
...
eden-1      | [2021-11-02 17:57:13,646: WARNING/MainProcess] on device:cpu
eden-1      | [2021-11-02 17:57:13,647: WARNING/MainProcess]
eden-1      |
eden-1      | [2021-11-02 17:57:13,647: WARNING/MainProcess] 0
eden-1      | [2021-11-02 17:57:13,647: WARNING/MainProcess]
eden-1      |
eden-1      | [2021-11-02 17:57:23,658: WARNING/MainProcess] 1
eden-1      | [2021-11-02 17:57:23,658: WARNING/MainProcess]
eden-1      |
eden-1      | [2021-11-02 17:57:33,672: WARNING/MainProcess] 2
eden-1      | [2021-11-02 17:57:33,672: WARNING/MainProcess]
eden-1      |
eden-1      | [2021-11-02 17:57:43,685: WARNING/MainProcess] 3
eden-1      | [2021-11-02 17:57:43,686: WARNING/MainProcess]
eden-1      |
...
```

If you run the command multiple times, you will see multiple edens picking up.

Run 100

```bash
for i in {1..100}; do curl http://localhost:8080/run -X POST -H "Content-Type: application/json" -d "{}"; done
```

To check on jobs, use flower: point your browser to http://localhost:5555/

The metrics are scraped with prometheus, to check on them (for example to plot the evolution of the metric `num_queue_jobs` http://localhost:9090/graph?g0.expr=num_queued_jobs&g0.tab=0&g0.stacked=0&g0.range_input=2h)

To simulate errors, just break one of the jobs. I prepared `server_for_docker_with_error.py` that was added to cotnainer

To make eden start it, in `docker-compose.yaml` after line 45 i added this line ` entrypoint: "python3 server_for_docker-with-error.py"` - telling `eden-3` to start with that.

Then I ran 100 jobs.

Wait until `eden-3` breaks.
