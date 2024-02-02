from nbclient import NotebookClient
from nbclient.util import ensure_async,run_sync
import nbformat
from nbformat import NotebookNode
from typing import Any
import json

class LibroNotebookClient(NotebookClient):
    def __init__(self, nb: NotebookNode, output_variable_path = None, output_notebook_path = None, parameters=None,km=None, raise_on_iopub_timeout=True, **kw):
        super().__init__(nb=nb, km=km, **kw)
        if isinstance(parameters, dict):
            self.parameters = json.dumps(parameters)
        else:
            self.parameters = parameters
        self.output_variable_path = output_variable_path
        self.output_notebook_path = output_notebook_path

    async def async_execute(self, reset_kc: bool = False, **kwargs: Any) -> NotebookNode:
        if reset_kc and self.owns_km:
            await self._async_cleanup_kernel()
        self.reset_execution_trackers()

        async with self.async_setup_kernel(**kwargs):
            assert self.kc is not None
            self.log.info("Executing notebook with kernel: %s" % self.kernel_name)
            msg_id = await ensure_async(self.kc.kernel_info())
            info_msg = await self.async_wait_for_reply(msg_id)
            if info_msg is not None:
                if "language_info" in info_msg["content"]:
                    self.nb.metadata["language_info"] = info_msg["content"]["language_info"]
                else:
                    raise RuntimeError(
                        'Kernel info received message content has no "language_info" key. '
                        "Content is:\n" + str(info_msg["content"])
                    )
            cell_allows_errors = (not self.force_raise_errors) and (self.allow_errors)
            await ensure_async(
                self.kc.execute(
                    f"__libro_input_dict__={self.parameters}\n", store_history=True, stop_on_error=not cell_allows_errors
                )
            )
            if self.output_variable_path is not None:
                await ensure_async(
                    self.kc.execute(
                        f"__libro_output__='{self.output_variable_path}'\n", store_history=True, stop_on_error=not cell_allows_errors
                    )
                )
            
            for index, cell in enumerate(self.nb.cells):
                await self.async_execute_cell(
                    cell, index, execution_count=self.code_cells_executed + 1
                )
                if self.output_notebook_path is not None:
                    with open(self.output_notebook_path, 'w', encoding='utf-8') as f:
                        nbformat.write(self.nb, f) 
            self.set_widgets_metadata()
        return self.output_variable_path

    execute = run_sync(async_execute)
