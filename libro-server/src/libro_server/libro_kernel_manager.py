from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager
from jupyter_server.gateway.managers import GatewayMappingKernelManager
from libro_core.config import libro_config

class LibroKernelManager(AsyncMappingKernelManager):
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

        kernel = self.get_kernel(kernel_id).client()
        if kernel:
            kernel.execute(
                code,
                silent=True
            )
        return kernel_id

class LibroGatewayMappingKernelManager(GatewayMappingKernelManager):
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

        kernel = self.get_kernel(kernel_id).client()
        if kernel:
            kernel.execute(
                code,
                silent=True
            )
        return kernel_id