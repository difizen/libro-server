import json
import os
from jupyter_server.base.handlers import APIHandler
from jupyter_server.auth.decorator import authorized, allow_unauthenticated
import requests
from tornado.web import HTTPError, authenticated
from libro_flow import execute_notebook, LibroNotebookClient
from jupyter_server.utils import ApiPath, to_os_path, to_api_path
from jupyter_core.utils import ensure_dir_exists
from contextlib import contextmanager
import errno
from traitlets import Unicode
import oss2


class ZxzHandler(APIHandler):

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
    async def get(self) -> None:
        # model = self.get_json_body()
        # if model is None:
        #     raise HTTPError(400, "can not get arguments")

        args = self.request.query_arguments
        arg_path = args.get('path', None)
        arg_path = b''.join(arg_path).decode('utf-8')
        if arg_path is None:
            raise IOError("Can not get file path")
        
        try:
            file_path = self._get_os_path(arg_path)
            config_path = '/config/config.txt'  # 文件路径
            with open(config_path, 'r', encoding='utf-8') as file:
                user_id = file.read()
            
            # user_id = '2088502728605001'
            # file_path = '/Users/brokun/github/libro-server/examples/a-test.jpeg'
            
            """
            上传文件到指定的URL。

            参数:
            url (str): 服务器URL。
            file_path (str): 要上传的本地文件路径。
            """
            # 打开文件
            with open(file_path, 'rb') as file:
                # 使用 requests 库发起 POST 请求
                files = {'file': file}
                response = requests.post(f"https://zxzcopilotbff-pre.alipay.com/api/libro/getDownloadUrl?userId={user_id}",  files=files)
            # 检查响应状态码
            if response.status_code == 200:
                print("文件上传成功:", response.text)
            else:
                print("文件上传失败:", response.status_code, response.text)
        except IOError as e:
            self.log.error("Failed to write file due to IOError %s", str(e))
        self.write(response.text)

