import type { NotebookOption } from '@difizen/libro-core';
import { VirtualizedManagerHelper } from '@difizen/libro-core';
import { CollapseServiceFactory, NotebookService } from '@difizen/libro-core';
import { LibroView, notebookViewFactoryId } from '@difizen/libro-core';
import {
  getOrigin,
  URI,
  useConfigurationValue,
  useInject,
  useObserve,
  view,
  ViewInstance,
  ViewOption,
} from '@difizen/mana-app';
import { inject, transient } from '@difizen/mana-app';

import {
  CellView,
  CustomDragLayer,
  DndContentProps,
  DndContext,
  DndList,
  ExecutableCellView,
  LibroJupyterView,
} from '@difizen/libro-jupyter';
import {
  FC,
  ReactNode,
  forwardRef,
  memo,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';
import { BackTop, Button } from 'antd';
import { ToTopOutlined } from '@ant-design/icons';
import classNames from 'classnames';
import React from 'react';
import { AppCellContainer } from './default-dnd-content';
import { DndCellItemRender } from './dnd-cell-item-render';

export const DndCellRender: FC<DndContentProps> = memo(function DndCellRender({
  cell,
  index,
  ...props
}: DndContentProps) {
  const observableCell = useObserve(cell);
  const instance = useInject<LibroView>(ViewInstance);
  const DndCellContainer = instance.dndContentRender;

  return (
    <DndCellContainer cell={observableCell} key={cell.id} index={index} {...props} />
  );
});

export const DndCellsRender = forwardRef<
  HTMLDivElement,
  { libroView: LibroView; addCellButtons: ReactNode }
>(function DndCellsRender(
  { libroView, addCellButtons }: { libroView: LibroView; addCellButtons: ReactNode },
  ref,
) {
  const LoadingRender = getOrigin(libroView.loadingRender);
  const virtualizedManagerHelper = useInject(VirtualizedManagerHelper);
  const virtualizedManager = virtualizedManagerHelper.getOrCreate(libroView.model);

  const cells = libroView.model.getCells().reduce<CellView[]>(function (a, b) {
    if (a.indexOf(b) < 0) {
      a.push(b);
    }
    return a;
  }, []);

  const [isVirtualList, setIsVirtualList] = useState<boolean>(false);
  const [isJudging, setIsJudging] = useState<boolean>(true);

  useEffect(() => {
    if (!libroView.model.isInitialized) {
      return;
    }

    let size = undefined;
    let path = undefined;

    // TODO: 类型处理
    const model = libroView.model as any;
    if (model.currentFileContents && model.currentFileContents.size) {
      size = parseFloat((model.currentFileContents.size / 1048576).toFixed(3)); // 单位MB
      path = model.currentFileContents.path || '';
    }

    setIsJudging(true);
    virtualizedManager
      .openVirtualized(cells.length, size, path)
      .then((willOpen) => {
        setIsVirtualList(willOpen);
        return;
      })
      .catch(() => {
        setIsVirtualList(false);
      })
      .finally(() => {
        setIsJudging(false);
      })
      .catch((e) => {
        //
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [virtualizedManager, libroView.model.isInitialized]);

  const isInitialized = libroView.model.isInitialized;
  const isLoading = !isInitialized || isJudging;
  const shouldRenderCells = isInitialized && !isJudging;

  return (
    <>
      <div className={classNames('libro-dnd-cells-container')} ref={ref}>
        {isLoading && <LoadingRender />}
        {shouldRenderCells && (
          <div style={{ height: '100%', overflow: 'visible' }}>
            {cells
              .filter((cell) => !cell.collapsedHidden)
              .map((cell, index) => (
                <DndCellRender cell={cell} key={cell.id} index={index} />
              ))}
          </div>
        )}
      </div>
    </>
  );
});

export const LibroAppComponent = memo(function LibroAppComponent() {
  const ref = useRef<HTMLDivElement | null>(null);
  const libroViewTopRef = useRef<HTMLDivElement>(null);
  const libroViewRightContentRef = useRef<HTMLDivElement>(null);
  const libroViewLeftContentRef = useRef<HTMLDivElement>(null);
  const libroViewContentRef = useRef<HTMLDivElement>(null);
  const instance = useInject<LibroView>(ViewInstance);

  const handleScroll = useCallback(() => {
    instance.cellScrollEmitter.fire();
    const cellRightToolbar = instance.container?.current?.getElementsByClassName(
      'libro-cell-right-toolbar',
    )[instance.model.activeIndex] as HTMLDivElement;
    const activeCellOffsetY =
      instance.activeCell?.container?.current?.getBoundingClientRect().y;
    const activeCellOffsetRight =
      instance.activeCell?.container?.current?.getBoundingClientRect().right;
    const activeOutput =
      ExecutableCellView.is(instance.activeCell) && instance.activeCell?.outputArea;
    const activeOutputOffsetBottom =
      activeOutput && activeOutput.length > 0
        ? activeOutput?.outputs[
            activeOutput.length - 1
          ].container?.current?.getBoundingClientRect().bottom
        : instance.activeCell?.container?.current?.getBoundingClientRect().bottom;
    const libroViewTopOffsetBottom =
      libroViewTopRef.current?.getBoundingClientRect().bottom;

    if (!cellRightToolbar) {
      return;
    }
    if (
      activeCellOffsetY !== undefined &&
      libroViewTopOffsetBottom !== undefined &&
      activeOutputOffsetBottom !== undefined &&
      activeCellOffsetY <= libroViewTopOffsetBottom + 12 &&
      activeOutputOffsetBottom >= libroViewTopOffsetBottom &&
      activeCellOffsetRight !== undefined
    ) {
      cellRightToolbar.style.cssText = `position:fixed;top:${
        libroViewTopOffsetBottom + 12
      }px;left:${activeCellOffsetRight + 44 - 34}px;right:unset;`;
    } else {
      cellRightToolbar.style.cssText = '  position: absolute;top: 0px;right: -44px;';
    }
  }, [instance]);

  return (
    <div
      className="libro-view-content"
      onScroll={handleScroll}
      ref={libroViewContentRef}
    >
      <div className="libro-view-content-left" ref={libroViewLeftContentRef}>
        <div className="libro-dnd-list-container">
          <DndContext>
            <CustomDragLayer />
            <DndCellsRender libroView={instance} addCellButtons={null} />
          </DndContext>
        </div>
      </div>
      <div className="libro-view-content-right" ref={libroViewRightContentRef}></div>
      <BackTop target={() => libroViewContentRef.current || document}>
        <div className="libro-totop-button">
          <Button shape="circle" icon={<ToTopOutlined />} />
        </div>
      </BackTop>
    </div>
  );
});

@transient()
@view(notebookViewFactoryId)
export class LibroAppView extends LibroJupyterView {
  override view = LibroAppComponent;
  dndContentRender: FC<DndContentProps> = AppCellContainer;
  dndItemRender: React.MemoExoticComponent<
    ForwardRefExoticComponent<DndItemProps & RefAttributes<HTMLDivElement>>
  > = DndCellItemRender;
  uri: URI;
  constructor(
    @inject(ViewOption) options: NotebookOption,
    @inject(CollapseServiceFactory) collapseServiceFactory: CollapseServiceFactory,
    @inject(NotebookService) notebookService: NotebookService,
    @inject(VirtualizedManagerHelper)
    virtualizedManagerHelper: VirtualizedManagerHelper,
  ) {
    super(options, collapseServiceFactory, notebookService, virtualizedManagerHelper);
  }
  get options() {
    return this.model.options;
  }
}
