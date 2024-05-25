import type { NotebookOption } from '@difizen/libro-core';
import { LibroView } from '@difizen/libro-core';
import {
  BaseView,
  prop,
  URI,
  useInject,
  view,
  ViewInstance,
  ViewOption,
  ViewRender,
} from '@difizen/mana-app';
import { inject, transient } from '@difizen/mana-app';

import {
  ExecutableCellView,
  LibroService,
  ServerConnection,
} from '@difizen/libro-jupyter';
import { memo, useRef } from 'react';

export const LibroHackthonComponent = memo(function LibroAppComponent() {
  const libroViewContentRef = useRef<HTMLDivElement>(null);
  const instance = useInject<LibroHackthonView>(ViewInstance);

  return (
    <div
      className="libro-view-content"
      ref={libroViewContentRef}
    >
        {
            instance.libroView?.model.cells.map(cell => {
                if(!cell.model.metadata['renderCellOutput']) return null;
                if(ExecutableCellView.is(cell) ){
                    return <ViewRender view={cell.outputArea}></ViewRender>
                }else{
                    return <ViewRender view={cell}></ViewRender>
                }
            })
        }
    
    </div>
  );
});

@transient()
@view('libro-hackthon')
export class LibroHackthonView extends BaseView {
  protected libroService: LibroService;
  override view = LibroHackthonComponent;
  declare uri: URI;

  @inject(ServerConnection) serverConnection: ServerConnection;

  @prop() libroView?: LibroView;

  @prop() executeMessage?: string;

  @prop() executing: boolean = false;

  @prop() executed: number;

  @prop() succeed?: boolean = undefined;

  @prop()
  runId: string;

  constructor(
    @inject(ViewOption) options: NotebookOption,
    @inject(LibroService) libroService: LibroService,
  ) {
    super();
    this.libroService = libroService;
    this.libroService.getOrCreateView(options).then((view) => {
      this.libroView = view;
    });
  }
  get options() {
    return this.libroView?.model.options;
  }
}
