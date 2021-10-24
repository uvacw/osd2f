# Deploying OSD2F as a container

## What is a container and why use it?

Containers, most populairly [docker containers](https://www.docker.com/resources/what-container) are ways
to package an application, making sure all dependencies and environment characteristics are wrapped
together. This makes containers ideal for deployment across different environments, without worrying
about OS compatibilities, libraries that need to be installed on servers etcetera. 

The popularity of containers as a deployment model is clear in the broad support. PaaS offerings such
as [Google app engine](https://cloud.google.com/appengine/docs/flexible), [Amazon ECS](https://aws.amazon.com/ecs/) 
and [Microsoft Azure Container Instances](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-quickstart)
support running arbitrary containers without requiring any advanced cloud management skills.

For more advanced setups, the common deployment infrastructure is [Kubernetes (k8s)](https://kubernetes.io/), a container orchestration platform that combines containers and allows for their deployment across
servers. 

### TL;DR: 
* containers make applications easy to move between servers
* containers are widely supported by cloud providers

## Creating an OSD2F container

### Building a test container

If you want to test whether the code still works after modifications:

```bash
docker build -t osd2f-test -f Dockerfile-test ./
```
If the build is succesfull, that means all tests have passed.
You can access the container by running it:

```bash
docker run -it osd2f-test bash
```

This is slower to build and contains more dependencies that are normally only used for development. This
is not the container specification that is meant for production deployments.

### Building a container for deployment

```bash
docker build -t osd2f -f Dockerfile ./ 
```

Running the container (using port 8000), the `-p` flag sets the host port of you machine to refer to the port of the container. The `-e` flags are used to set environment variables. Note that production instances
always require a session secret. The example here is not suited for production, as you should avoid allowing researcher access through basic authentication and the database is an in-memory database that
will be reset to empty every time the container is restarted. 

```bash
docker run -it \
    -e OSD2F_MODE="Production" \
    -e OSD2F_BASIC_AUTH='user;pass' \
    -e OSD2F_SECRET="a big secret here" \
    -e OSD2F_DB_URL="sqlite://:memory:" \
    -p 8000:8000 \
    osd2f
```
You should be able to reach the server now at http://localhost:8000/

## Deploying containers to production

Container use in production is strongly related to the solution you will be using. Some deployment platforms enable you to upload the docker image through a CLI tool or as part of a CI/CD interface. Other systems such as [Kubernetes (k8s)](https://kubernetes.io/) require the docker image to be available in a repository.

You can push the container image to a repository of your choosing. The syntax ([as specified by Docker](https://docs.docker.com/docker-hub/repos/)) is the following: 

```bash
docker push <hub-user>/<repo-name>:<tag>
```

Whether and which repository to use depends on the the platform you choose to use for the deployment. Note that running the container on a single server will risk limited availability (downtime when this server experiences issues) and comes at considerable operational overhead (configuring security, keeping the systrem up-to-date, backing up data etcetera). 

