import { LibroJupyterView, LibroView } from '@difizen/libro-jupyter';
import {
  BaseView,
  prop,
  URI,
  useInject,
  useObserve,
  view,
  ViewInstance,
  ViewManager,
  ViewRender,
} from '@difizen/mana-app';
import { inject, transient } from '@difizen/mana-app';
import qs from 'query-string';
import {
  ExecutableCellView,
  LibroService,
  ServerConnection,
} from '@difizen/libro-jupyter';
import { memo, useEffect, useRef } from 'react';
import './index.less';
import React from 'react';

export const LibroInterpreterComponent = memo(function LibroAppComponent() {
  const libroViewContentRef = useRef<HTMLDivElement>(null);
  const instance = useInject<LibroInterpreterView>(ViewInstance);
  const queryParams = qs.parse(window.location.search);
  const libroView = useObserve(instance.libroView);
  const filePath = queryParams['path'];
  
  useEffect(() => {
    if (filePath && typeof filePath === 'string') {
      instance.path = filePath;
    }
  }, [filePath]);

  if (!queryParams['path']) {
    return <div>需要指定要渲染的文件</div>;
  }

  return (
    <div
      className="libro-view-content"
      ref={libroViewContentRef}
    >
        {
            libroView?.model.cells.map(cell => {
                if(ExecutableCellView.is(cell) ){
                    return <ViewRender view={cell.outputArea}></ViewRender>
                }else{
                    return null
                }
            })
        }
    
    </div>
  );
});

@transient()
@view('libro-interpreter')
export class LibroInterpreterView extends BaseView {
  override view = LibroInterpreterComponent;
  declare uri: URI;

  @inject(ServerConnection) serverConnection: ServerConnection;

  @inject(ViewManager) viewManager: ViewManager;

  @inject(LibroService) libroService: LibroService;

  @prop() libroView?: LibroView;

  protected _path: string;
  get path(): string {
    return this._path;
  }
  set path(v: string) {
    this._path = v;
    this.update();
  }

  update = async () => {
    if (!this.path) return;
    document.title = `interaction: ${this.path}`;
    this.libroView = await this.viewManager.getOrCreateView(LibroJupyterView, {
      resource: this.path,
    });
  };
}
