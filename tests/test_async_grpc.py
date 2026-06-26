import asyncio

import grpc
import pytest
import pytest_asyncio

from labgrid.remote.coordinator import Coordinator
from labgrid.remote.generated import labgrid_coordinator_pb2
from labgrid.remote.generated import labgrid_coordinator_pb2_grpc

@pytest_asyncio.fixture
async def coordinator():
    loop = asyncio.get_running_loop()
    coordinator = Coordinator()
    channel_options = [
        ("grpc.so_reuseport", 0),  # no load balancing
        ("grpc.keepalive_time_ms", 10000),  # 10 seconds
        ("grpc.keepalive_timeout_ms", 10000),  # 10 seconds
        ("grpc.http2.ping_timeout_ms", 15000),  # 15 seconds
        ("grpc.http2.min_ping_interval_without_data_ms", 5000),
        ("grpc.http2.max_pings_without_data", 0),  # no limit
        ("grpc.keepalive_permit_without_calls", 1),  # allow keepalive pings even when there are no calls
    ]
    server = grpc.aio.server(
        options=channel_options,
    )
    labgrid_coordinator_pb2_grpc.add_CoordinatorServicer_to_server(coordinator, server)
    server.add_insecure_port("[::]:20408")
    await server.start()
    yield coordinator
    await server.stop(5)

@pytest.mark.asyncio
async def test_async_simple_coordinator_test(coordinator):
    print("Hello from test")
    print(coordinator.places)
    print(coordinator.reservations)
    print(coordinator.poll_tasks)
    print(coordinator.lock)
    assert True
