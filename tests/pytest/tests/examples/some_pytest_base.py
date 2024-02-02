from pathlib import Path

import pytest

import quickbolt.utils.directory as dh
from quickbolt.clients import AioGPRC, AioRequests
from quickbolt.pytest import CorePytestBase
from tests.client.gprc.test_async_call import check_server


class SomePytestBase(CorePytestBase):
    file_path = Path(__file__)
    root_dir = str(Path().joinpath(*file_path.parts[:-3]))

    # core_setup_teardown is from CorePytestBase - it will exist at runtime
    @pytest.fixture(autouse=True, scope="class")
    async def setup_teardown(self, core_setup_teardown):
        self.aio_requests = AioRequests(root_dir=self.root_dir)
        self.aio_grpc = AioGPRC(root_dir=self.root_dir)
        self.debug = "Some value"

        for k, v in self.__dict__.items():
            setattr(SomePytestBase, k, v)

        process = check_server()

        yield

        self.csv_path = self.aio_requests.csv_path
        run_info_path = self.aio_requests.logging.run_info_path
        expanded_dir = await dh.expand_directory(run_info_path)

        files = ["/".join(p[-2:]) for e in expanded_dir if (p := Path(e).parts)]
        expected_files = [
            "pytest/run_info",
            "run_info/run_logs",
            "run_logs/examples",
            "examples/get",
            "get/fail",
            "get/pass",
            "pass/get_scrubbed.csv",
            "pass/get.csv",
            "pass/get.log",
        ]
        assert all(e in files for e in expected_files)

        logs = [r async for r in self.aio_requests.logging.read_log_file()]
        checks = ["making", "made", "returning", "batch duration"]
        assert all(c in logs[i].lower() for i, c in enumerate(checks))

        process.kill()
