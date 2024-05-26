import json
import os
from jupyter_server.base.handlers import APIHandler
from jupyter_server.auth.decorator import authorized, allow_unauthenticated
from libro_server.hackthon.agent import MyCustomHandler,agent
from tornado.web import HTTPError, authenticated
from libro_flow import execute_notebook, LibroNotebookClient
from jupyter_server.utils import ApiPath, to_os_path, to_api_path
from jupyter_core.utils import ensure_dir_exists
from contextlib import contextmanager
import errno
from traitlets import Unicode
import uuid
from libro_server.hackthon_globals import NotebooksInfo, run_id_to_notebooks,run_id_to_agent_task
from langchain_core.runnables.config import RunnableConfig
import asyncio

class LibroChatHandler(APIHandler):
    executors: dict[str, LibroNotebookClient] = {}

    execution_dir = "execution"

    def _get_os_path(self, path):
        """Given an API path, return its file system path.

        Parameters
        ----------
        path : str
            The relative API path to the named file.

        Returns
        -------
        path : str
            Native, absolute OS path to for a file.

        Raises
        ------
        404: if path is outside root
        """
        self.log.debug("Reading path from disk: %s", path)
        root = os.path.abspath(
            self.contents_manager.root_dir
        )  # type:ignore[attr-defined]
        # to_os_path is not safe if path starts with a drive, since os.path.join discards first part
        if os.path.splitdrive(path)[0]:
            raise HTTPError(404, "%s is not a relative API path" % path)
        os_path = to_os_path(ApiPath(path), root)
        # validate os path
        # e.g. "foo\0" raises ValueError: embedded null byte
        try:
            os.lstat(os_path)
        except OSError:
            # OSError could be FileNotFound, PermissionError, etc.
            # those should raise (or not) elsewhere
            pass
        except ValueError:
            raise HTTPError(404, f"{path} is not a valid path") from None

        if not (os.path.abspath(os_path) + os.path.sep).startswith(root):
            raise HTTPError(404, "%s is outside root contents directory" % path)
        return os_path

    @contextmanager
    def perm_to_403(self, os_path=""):
        """context manager for turning permission errors into 403."""
        try:
            yield
        except OSError as e:
            if e.errno in {errno.EPERM, errno.EACCES}:
                # make 403 error message without root prefix
                # this may not work perfectly on unicode paths on Python 2,
                # but nobody should be doing that anyway.
                if not os_path:
                    os_path = e.filename or "unknown file"
                path = to_api_path(os_path)  # type:ignore[attr-defined]
                raise HTTPError(403, "Permission denied: %s" % path) from e
            else:
                raise

    # Checkpoint-related utilities
    def result_path(self, path: str):
        path = path.strip("/")
        parent, name = ("/" + path).rsplit("/", 1)
        parent = parent.strip("/")
        basename, ext = os.path.splitext(name)
        filename = f"{basename}{ext}"
        os_path = self._get_os_path(path=parent)
        execution_dir = os.path.join(os_path, self.execution_dir)
        with self.perm_to_403():
            ensure_dir_exists(execution_dir)
        execution_path = os.path.join(execution_dir, filename)
        return execution_path

    @authenticated
    @allow_unauthenticated
    async def post(self) -> None:
        self.set_header("Content-Type", "application/json")
        model = self.get_json_body()
        if model is None:
            raise HTTPError(400, "can not get arguments")
        input = model.get("input")
        print(input)
        args = model.get("args")

        run_id = uuid.uuid4()
        print(run_id)
        callback = MyCustomHandler(post_method=self.finish)
        runconfig = RunnableConfig(
            callbacks=[callback]
        )
        run_id = str(uuid.uuid4())
        if input is None:
            raise HTTPError(400, "input is missing")
        if not isinstance(input, str):
            raise HTTPError(400, "input is invalid")
        task = asyncio.create_task(agent.invoke({"input": input}, runconfig))
        print("task",task)
        run_id_to_agent_task[run_id] = task

    @authenticated
    @allow_unauthenticated
    async def get(self) -> None:
        run_id = self.request.query_arguments.get("runId")
        if run_id is not None:
            run_id = "".join(map(bytes.decode, run_id))
        res = None
        if isinstance(run_id, str):
            notebooks_res:NotebooksInfo = run_id_to_notebooks.get(run_id)
            print('notebooks_res',notebooks_res)
            if notebooks_res is None:
                raise HTTPError(400, "run_id is invalid")
            notebooks_clients= notebooks_res.get("render_notebooks").stack
            if notebooks_clients is None:
                raise HTTPError(400, "notebooks_clients is None")
            notebooks = []
            print("chat get before")
            for client in notebooks_clients:
                notebooks.append(client.get_status().model_dump_json())
                print("chat get after")
            res = {
                "id":run_id,
                "status":notebooks_res.get("status"),
                "notebooks":notebooks
            }
        else:
            raise HTTPError(400, "run_id is invalid")
        if res is None:
            raise HTTPError(400, "this run_id cant find notebook")
        self.write(json.dumps(res))
