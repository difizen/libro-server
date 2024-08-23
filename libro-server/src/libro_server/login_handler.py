import json
from jupyter_server.base.handlers import APIHandler
from jupyter_server.auth.decorator import allow_unauthenticated
from tornado.web import HTTPError
from jupyter_server.utils import to_api_path
from contextlib import contextmanager
import os
import errno

class LoginHandler(APIHandler):

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
    async def post(self) -> bool:
            model = self.get_json_body()
            if model is None:
                raise HTTPError(400, "can not get arguments")
            user_id = model.get("user_id")
            host_name = model.get("host_name")
            real_host_name = os.getenv('HOSTNAME')
            file_path = "/config/config.txt"
            if host_name == real_host_name:
                # 创建文件并将字符串写入
                with open(file_path, 'w') as file:
                    file.write(user_id)
            else:
                raise HTTPError(400, "pod host name is not correct")


        
        
        
