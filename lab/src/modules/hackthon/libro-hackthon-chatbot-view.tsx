import {
  BaseView,
  prop,
  singleton,
  timeout,
  URI,
  useInject,
  view,
  ViewInstance,
  ViewManager,
} from '@difizen/mana-app';
import { inject } from '@difizen/mana-app';
import { ServerConnection } from '@difizen/libro-jupyter';
import { memo, useRef } from 'react';
import { Button } from 'antd';

interface LibroExecution {
  id: string;
  current_index: number;
  cell_count: number;
  code_cells_executed: number;
  start_time: string;
  end_time: string;
  execute_result_path: string;
  execute_record_path: string;
}
interface LibroChat {
    id: string;
    status:'loading'|'success'|'fail'
    render_notebooks:LibroExecution[];
}

export const LibroHackthonComponent = memo(function LibroAppComponent() {
  const libroViewContentRef = useRef<HTMLDivElement>(null);
  const instance = useInject<LibroHackthonChatbotView>(ViewInstance);

  return (
    <div
      className="libro-chatbot"
      ref={libroViewContentRef}
    >
        <Button onClick={()=>{
            instance.postChat('请问玄学是什么？');
        }}></Button>    
    </div>
  );
});

@singleton()
@view('libro-hackthon-chatbot')
export class LibroHackthonChatbotView extends BaseView {
  override view = LibroHackthonComponent;
  declare uri: URI;

  @inject(ServerConnection) serverConnection: ServerConnection;

  @inject(ViewManager) viewManager: ViewManager;

  @prop() executeMessage?: string;

  @prop() executing: boolean = false;

  @prop() executed: number;

  @prop() succeed?: boolean = undefined;

  @prop() curNotebook?: string;

  postChat = async (input:string,args?: any)=>{
    this.serverConnection.settings.baseUrl;
    try {
      const res = await this.serverConnection.makeRequest(
        `${this.serverConnection.settings.baseUrl}libro/api/chat`,
        {
          method: 'POST',
          body: JSON.stringify({ args, input }),
        },
      );
      const result = await res.json();
      this.executing = true;
      this.updateStatus(result.runId);
    } catch (ex) {
      console.log(ex);
    }
  }

  doUpdateStatus = async (runId:string) => {
    const res = await this.serverConnection.makeRequest(
      `${this.serverConnection.settings.baseUrl}libro/api/chat?runId=${runId}`,
      {
        method: 'GET',
      },
    );
    const result = (await res.json()) as LibroChat;
    console.log("🚀 ~ LibroHackthonChatbotView ~ doUpdateStatus= ~ result:", result)
    if (result.status==="success") {
      this.executing = false;
      return true;
    }
    return false;
  };

  updateStatus = async (runId:string): Promise<void> => {
    if (!(await this.doUpdateStatus(runId))) {
      await timeout(1000);
      return this.updateStatus(runId);
    } else {
      // this.updateExecutionResult();
    }
  };
}
