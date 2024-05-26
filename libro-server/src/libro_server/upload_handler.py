import json
import os
from jupyter_server.base.handlers import APIHandler
from jupyter_server.auth.decorator import authorized, allow_unauthenticated
from tornado.web import HTTPError, authenticated
from libro_flow import execute_notebook, LibroNotebookClient
from jupyter_server.utils import ApiPath, to_os_path, to_api_path
from jupyter_core.utils import ensure_dir_exists
from contextlib import contextmanager
import errno
from traitlets import Unicode
import oss2


class UploadHandler(APIHandler):

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
            raise HTTPError(
                404, "%s is outside root contents directory" % path)
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

    @allow_unauthenticated
    async def post(self) -> None:
        self.set_header("Content-Type", "application/json")
        # model = self.get_json_body()
        # if model is None:
        #     raise HTTPError(400, "can not get arguments")

        fileinfo = self.request.files["file"][0]
        filename = fileinfo["filename"]
        try:
            # TODO: AK
            auth = oss2.Auth(
                access_key_id="",
                access_key_secret="",
            )
            bucket = oss2.Bucket(
                auth, "http://oss-cn-beijing.aliyuncs.com", "nl2quant")
            result = bucket.put_object(filename, fileinfo["body"])
            if result.status == 200:
                self.log.info(
                    "%s uploaded %s, saved as %s",
                    str(self.request.remote_ip),
                    filename,
                    filename,
                )
            else:
                raise IOError("upload to oss failed")
        except IOError as e:
            self.log.error("Failed to write file due to IOError %s", str(e))
        self.write(json.dumps({"filename": filename}))

    @allow_unauthenticated
    async def put(self) -> None:
        self.set_header("Content-Type", "application/json")
        model = self.get_json_body()
        if model is None:
            raise HTTPError(400, "can not get arguments")

        filename = model.get("filename")
        try:
            os_path = self._get_os_path(filename)
            # TODO: AK
            auth = oss2.Auth(
                access_key_id="",
                access_key_secret="",
            )
            bucket = oss2.Bucket(
                auth, "http://oss-cn-beijing.aliyuncs.com", "nl2quant")
            with open(os_path, "rb") as fileobj:
                result = bucket.put_object(filename, fileobj)
                if result.status == 200:
                    self.log.info(
                        "%s uploaded %s, saved as %s",
                        str(self.request.remote_ip),
                        filename,
                        filename,
                    )
                else:
                    raise IOError("upload to oss failed")
        except IOError as e:
            self.log.error("Failed to write file due to IOError %s", str(e))
        self.write(json.dumps({"filename": filename}))
