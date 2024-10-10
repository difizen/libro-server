import logging
from jupyter_server.services.kernels.kernelmanager import ServerKernelManager
from libro_core.config import libro_config
logger = logging.getLogger(__name__)
class LibroKernelManager(ServerKernelManager):

    async def start_kernel(self,**kw):
        kernel_id = await super(LibroKernelManager,self).start_kernel(**kw)
        # 在内核启动时执行特定代码
        extensions = libro_config.get_config().get("jpserver_extensions",{})
        commands = []

        # 遍历扩展，生成相应的 %load_ext 或 %unload_ext 命令
        for ext, enabled in extensions.items():
            command = f"%load_ext {ext}" if enabled else f"%unload_ext {ext}"
            commands.append(command)

        # 使用 join 方法将所有命令连接成一个字符串
        code = "\n".join(commands)
        self.log.debug("Init execution codes: %r", code)

        client = self.blocking_client()
        try:
            client.start_channels()
            client.wait_for_ready(30)
            client.execute(code)

        except Exception as e:
            logger.warn("failed to run code with kernel, exp: %s" % e)
        finally:
            if client:
                client.stop_channels()
        return kernel_id

    async def restart_kernel(self, *args, **kwargs):
        await super(LibroKernelManager,self).restart_kernel(*args, **kwargs)
        # 在内核启动时执行特定代码
        extensions = libro_config.get_config().get("jpserver_extensions",{})
        commands = []

        # 遍历扩展，生成相应的 %load_ext 或 %unload_ext 命令
        for ext, enabled in extensions.items():
            command = f"%load_ext {ext}" if enabled else f"%unload_ext {ext}"
            commands.append(command)

        # 使用 join 方法将所有命令连接成一个字符串
        code = "\n".join(commands)
        self.log.debug("Init execution codes: %r", code)

        client = self.blocking_client()
        try:
            client.start_channels()
            client.wait_for_ready(30)
            client.execute(code)

        except Exception as e:
            logger.warn("failed to run code with kernel, exp: %s" % e)
        finally:
            if client:
                client.stop_channels()