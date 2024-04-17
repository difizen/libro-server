import React from 'react';
import {
  view,
  ViewOption,
  transient,
  useInject,
  ViewInstance,
  inject,
  prop,
} from '@difizen/mana-app';

import type { IWidgetViewProps } from '@difizen/libro-widget';
import { WidgetView } from '@difizen/libro-widget';
import { forwardRef, useCallback, useMemo } from 'react';
import { LibroContextKey } from '@difizen/libro-core';
import { RJSFSchema, SubmitButtonProps } from '@rjsf/utils';
import Form from '@rjsf/antd';
import validator from '@rjsf/validator-ajv8';
import './index.less';

function SubmitButton(props: SubmitButtonProps) {
  return null;
}

export const LibroSchemaFormWidgetComponent = forwardRef<HTMLDivElement>(
  (props, ref) => {
    const widgetView = useInject<LibroSchemaFormtWidget>(ViewInstance);

    const schema = useMemo(() => {
      try {
        return JSON.parse(widgetView.schema) as RJSFSchema;
      } catch (e) {
        return {};
      }
    }, [widgetView.schema]);

    const value = useMemo(() => {
      try {
        return JSON.parse(widgetView.value);
      } catch (e) {
        // console.error(e);
        return {};
      }
    }, [widgetView.value]);

    const handleChange = useCallback(
      (values: any) => {
        const data = {
          buffer_paths: [],
          method: 'update',
          state: { value: JSON.stringify(values.formData) },
        };
        widgetView.send(data);
      },
      [widgetView],
    );

    if (widgetView.isCommClosed) {
      return null;
    }

    return (
      <div className="libro-widget-schema-form" ref={ref}>
        <Form
          schema={schema}
          validator={validator}
          onChange={handleChange}
          onSubmit={() => console.log('submitted')}
          onError={() => console.log('errors')}
          templates={{ ButtonTemplates: { SubmitButton } }}
        />
      </div>
    );
  },
);

@transient()
@view('libro-widget-schema-form-view')
export class LibroSchemaFormtWidget extends WidgetView {
  override view = LibroSchemaFormWidgetComponent;

  schema: string;

  @prop() value: string;

  constructor(
    @inject(ViewOption) props: IWidgetViewProps,
    @inject(LibroContextKey) libroContextKey: LibroContextKey,
  ) {
    super(props, libroContextKey);
    this.schema = props.attributes.schema;
    this.value = props.attributes.value;
  }
}
