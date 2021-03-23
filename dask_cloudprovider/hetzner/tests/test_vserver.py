import pytest

import dask

hetzner = pytest.importorskip("hcloud")

from dask_cloudprovider.hetzner.vserver import HetznerCluster
from dask.distributed import Client
from distributed.core import Status


async def skip_without_credentials(config):
    if config.get("token") is None:
        pytest.skip(
            """
        You must configure a Hetzner API token to run this test.

        Either set this in your config

            # cloudprovider.yaml
            cloudprovider:
              hetzner:
                token: "yourtoken"

        Or by setting it as an environment variable

            export DASK_CLOUDPROVIDER__HETZNER__TOKEN="yourtoken"

        """
        )


@pytest.fixture
async def config():
    return dask.config.get("cloudprovider.hetzner", {})


@pytest.fixture
async def cluster(config):
    await skip_without_credentials(config)
    async with HetznerCluster(asynchronous=True) as cluster:
        yield cluster


@pytest.fixture
async def cluster_rapids(config):
    await skip_without_credentials(config)
    async with HetznerCluster(
        asynchronous=True,
        docker_image="rapidsai/rapidsai:cuda10.1-runtime-ubuntu18.04-py3.8",
    ) as cluster:
        yield cluster


@pytest.fixture
async def cluster_prefect(config):
    await skip_without_credentials(config)
    async with HetznerCluster(
        asynchronous=True,
        docker_image="prefecthq/prefect:0.14.11",
    ) as cluster:
        yield cluster


@pytest.mark.asyncio
async def test_init():
    cluster = HetznerCluster(asynchronous=True)
    assert cluster.status == Status.created


@pytest.mark.asyncio
@pytest.mark.timeout(600)
async def test_create_cluster(cluster):
    assert cluster.status == Status.running

    cluster.scale(1)
    await cluster
    assert len(cluster.workers) == 1

    async with Client(cluster, asynchronous=True) as client:

        def inc(x):
            return x + 1

        assert await client.submit(inc, 10).result() == 11


@pytest.mark.asyncio
@pytest.mark.timeout(600)
async def test_create_cluster_rapids(cluster_rapids):
    assert cluster_rapids.status == Status.running

    cluster_rapids.scale(1)
    await cluster_rapids
    assert len(cluster_rapids.workers) == 1

    async with Client(cluster_rapids, asynchronous=True) as client:

        def f():
            import cupy

            return float(cupy.random.random(100).mean())

        assert await client.submit(f).result() < 1


@pytest.mark.asyncio
async def test_get_cloud_init():
    cloud_init = HetznerCluster.get_cloud_init(
        docker_args="--privileged",
    )
    assert " --privileged " in cloud_init
