# services/code_runner.py
import uuid
import os
import shutil
import logging
import docker
from docker.errors import DockerException, ContainerError
from services.exceptions import APIError, NetworkError

logger = logging.getLogger(__name__)

# Defaults (can be tuned)
DEFAULT_IMAGE = os.getenv("CODE_SANDBOX_IMAGE", "python:3.12-slim")
DEFAULT_TIMEOUT = int(os.getenv("CODE_RUN_TIMEOUT", 5))  # seconds
DEFAULT_MEM_LIMIT = os.getenv("CODE_RUN_MEM", "128m")     # docker mem limit
DEFAULT_CPU_SHARES = int(os.getenv("CODE_RUN_CPU_SHARES", 64))  # relative

class CodeRunner:
    def __init__(self, image: str = DEFAULT_IMAGE):
        self.image = image
        try:
            self.client = docker.from_env()
        except DockerException as e:
            logger.exception("Docker client init failed: %s", e)
            self.client = None

    def run_python(self, code: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Run Python code inside a short-lived container and return dict with stdout/stderr/exit_code.
        Security notes:
          - No network (network_disabled=True)
          - Memory / CPU limits applied
          - Filesystem is ephemeral and removed after run
        """
        if not self.client:
            raise APIError("Docker client not available on host")

        workdir = f"/tmp/learnbot_code_{uuid.uuid4().hex}"
        host_dir = os.path.join("/tmp", f"learnbot_host_{uuid.uuid4().hex}")
        os.makedirs(host_dir, exist_ok=True)
        fname = os.path.join(host_dir, "main.py")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(code)

        container = None
        try:
            # Pull image if missing (may take time first run)
            try:
                self.client.images.pull(self.image)
            except Exception:
                # ignore pull failures (image may exist locally)
                pass

            # run container
            container = self.client.containers.run(
                self.image,
                command=["python", "/work/main.py"],
                volumes={host_dir: {'bind': '/work', 'mode': 'ro'}},
                working_dir="/work",
                detach=True,
                network_disabled=True,
                mem_limit=DEFAULT_MEM_LIMIT,
                cpu_shares=DEFAULT_CPU_SHARES,
                stderr=True,
                stdout=True,
                remove=False,  # we'll remove explicitly
            )

            try:
                res = container.wait(timeout=timeout)
            except Exception:
                # try to stop & remove container on timeout
                try:
                    container.kill()
                except Exception:
                    pass
                raise APIError("Code execution timed out")

            status = res.get("StatusCode", 1) if isinstance(res, dict) else getattr(res, "StatusCode", 1)
            logs = container.logs(stdout=True, stderr=True, stream=False)
            output = logs.decode("utf-8", errors="replace") if isinstance(logs, (bytes, bytearray)) else str(logs)

            return {
                "stdout": output,
                "stderr": "" if status == 0 else output,
                "returncode": status
            }

        except ContainerError as ce:
            logger.exception("ContainerError: %s", ce)
            raise APIError(f"Container error: {ce}")
        except DockerException as de:
            logger.exception("Docker exception: %s", de)
            raise APIError(f"Docker error: {de}")
        finally:
            # cleanup container & host_dir
            try:
                if container:
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass
            finally:
                try:
                    shutil.rmtree(host_dir, ignore_errors=True)
                except Exception:
                    pass
