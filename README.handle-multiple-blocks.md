# How to Simulate Eden in Production with Multiple BLocks

We have multiple eden instances in production.

To simulate this, I prepared a `docker-compose.yaml` file that starts locally the folowing containers:

- 3 x `instances of eden` each running a _diffent_ generator (`block1.py`,`block2.py`,`block3.py`)
- same `redis` to serve the edens
- `nginx` load balancer for eden instances.
- `flower` to see what is happening in celery
- `prometheus` to see the metrics exposed by eden

To build eden and start the :point_up: stack:

```bash
docker compose up --build
```

The window where you run `docker-compose` will show logs from all containers.

`Ctrl-C` will stop all. If you don't change eden code (e.g. change only generators), you don't have to rebuild, run without `--build` and will go faster.

The exposed ports:

Eden "load balancer" is behind port `8080`, it will route requests randomly to to `eden-1`, `eden-2`, `eden-3` containers. (you can reach them separately on `5001`, `5002`, `5003`)

I used `name` variable to specify the block. To run `block1` issue :

```bash
curl http://localhost:8080/run -X POST -H "Content-Type: application/json" -d "{\"name\":\"1\"}"
```

You'll get a token back.

What happened is that one of the edens picked it up **but eden1 ran it**

If you run the command multiple times, you will see multiple edens picking up, but only eden1 running it!

Run 100 if you feel like.

```bash
for i in {1..100}; do curl http://localhost:8080/run -X POST -H "Content-Type: application/json" -d "{}"; done
```

To check on jobs, use flower: point your browser to http://localhost:5555/

# Metrics

The metrics are scraped with prometheus, to check on them (for example to plot the evolution of the metric `num_queue_jobs` http://localhost:9090/graph?g0.expr=num_queued_jobs&g0.tab=0&g0.stacked=0&g0.range_input=2h)
