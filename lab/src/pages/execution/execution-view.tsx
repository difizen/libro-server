import React, { useCallback, useEffect, useRef } from 'react';
import {
  view,
  singleton,
  BaseView,
  ViewInstance,
  useInject,
  inject,
  prop,
  useObserve,
  URI,
  ViewRender,
} from '@difizen/mana-app';
import { forwardRef } from 'react';
import qs from 'query-string';
import { Button } from 'antd';
import Form from '@rjsf/antd';
import validator from '@rjsf/validator-ajv8';
import { RJSFSchema, SubmitButtonProps } from '@rjsf/utils';
import { BoxPanel } from '@difizen/mana-react';

import './index.less';
import { LibroFileService, LibroService, LibroView } from '@difizen/libro-jupyter';
import { IChangeEvent } from '@rjsf/core';

function SubmitButton(props: SubmitButtonProps) {
  return (
    <Button type="primary" htmlType="submit">
      Submit
    </Button>
  );
}

export const LibroExecutionComponent = forwardRef<HTMLDivElement>((props, ref) => {
  const formRef = useRef<Form<any, RJSFSchema, any> | null>(null);
  const instance = useInject<LibroExecutionView>(ViewInstance);
  const queryParams = qs.parse(window.location.search);
  const filePath = queryParams['path'];
  const libroView = useObserve(instance.libroView);
  useEffect(() => {
    if (filePath && typeof filePath === 'string') {
      instance.path = filePath;
    }
  }, [filePath]);

  useEffect(() => {
    if (libroView?.model.metadata) {
      const metadata = libroView?.model.metadata;
      if (metadata && metadata['args']) {
        instance.schema = metadata['args'];
        return;
      }
    }
    instance.schema = undefined;
  }, [libroView?.model.isInitialized]);

  const onSub = (data: IChangeEvent<any, RJSFSchema, any>) => {
    const formData = data.formData;
    instance.execute(formData);
  };

  if (!queryParams['path']) {
    return <div>需要指定要执行的文件</div>;
  }
  return (
    <div className="libro-execution-container" ref={ref}>
      <BoxPanel className="libro-execution-container-wrapper" direction="left-to-right">
        <BoxPanel.Pane className="libro-execution-container-left">
          {instance.resultView && <ViewRender view={instance.resultView}></ViewRender>}
        </BoxPanel.Pane>
        <BoxPanel.Pane className="libro-execution-container-right" flex={1}>
          <div>
            {instance.schema && (
              <Form
                ref={formRef}
                schema={instance.schema}
                validator={validator}
                onSubmit={onSub}
                templates={{ ButtonTemplates: { SubmitButton } }}
              />
            )}
          </div>
        </BoxPanel.Pane>
      </BoxPanel>
    </div>
  );
});

@singleton()
@view('libro-execution-view')
export class LibroExecutionView extends BaseView {
  @inject(LibroFileService) fileService: LibroFileService;
  @inject(LibroService) libroService: LibroService;
  override view = LibroExecutionComponent;

  @prop()
  libroView: LibroView | undefined;

  @prop()
  schema: any;

  @prop()
  resultView: LibroView | undefined;

  protected _path: string;
  get path(): string {
    return this._path;
  }
  set path(v: string) {
    this._path = v;
    this.update();
  }

  update = async () => {
    this.schema = undefined;
    if (!this.path) return;
    document.title = `execution: ${this.path}`;
    this.libroView = await this.libroService.getOrCreateView({
      resource: this.path,
    });
    this.updateExecutionResult();
  };

  updateExecutionResult = async () => {
    try {
      const file = new URI(this.path);
      const baseName = file.path.base;
      const resultUri = URI.resolve(file, `../execution/${baseName}`);
      const resultPath = resultUri.path.toString();
      const tryRead = await this.fileService.read(resultPath);
      if (tryRead) {
        this.resultView = await this.libroService.getOrCreateView({
          resource: resultPath,
        });
      }
    } catch (e) {}
  };

  execute = (args: any) => {};
}
