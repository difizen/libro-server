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

interface IRenderNotebook {
    file_path:string;
    last_modified:string
}
interface LibroChat {
    id: string;
    current_notebook_path: string;
    status:'loading'|'success'|'fail'
    start_time: string;
    end_time: string;
    render_notebooks:IRenderNotebook[];
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
            instance.postChat('LibroHackthonChatbotView');
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
    this.curNotebook = result.current_notebook_path;
    if (result.end_time) {
      this.executing = false;
      return true;
    }
    return false;
  };

  updateStatus = async (runId:string): Promise<void> => {
    if (!(await this.doUpdateStatus(runId))) {
      await timeout(1000);
    //   return this.updateStatus(runId);
    } else {
    //   this.updateExecutionResult();
    }
  };
}
