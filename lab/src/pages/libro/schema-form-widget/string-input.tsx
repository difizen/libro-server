import React, { useCallback, useState } from 'react';
import { Input } from 'antd';
import classNames from 'classnames';
import './string-input.less';

type Props = {
  className?: string;
  style?: React.CSSProperties;
  value?: string;
  onChange?: (val: string) => void;
  placeholder?: string;
  renderProps?: Record<string, any>;
};

export const StringInput = (props: Props) => {
  const { className, style, value, onChange, renderProps } = props;
  const [messageVisible, setMessageVisible] = useState<boolean>(false);

  const onChangeValue = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e.target.value);
      const pattern = renderProps?.['pattern'];
      const patterMessage = renderProps?.['patternMessage'];
      if (pattern && patterMessage) {
        try {
          const reg = new RegExp(pattern);
          const visible = !reg.test(e.target.value);
          setMessageVisible(visible);
        } catch (err) {
          setMessageVisible(false);
        }
      }
    },
    [onChange, renderProps],
  );

  return (
    <div className={classNames('schema-form-widget-container', className)}>
      <Input style={style} value={value} onChange={onChangeValue} {...renderProps} />
      {messageVisible && renderProps?.['patternMessage'] && (
        <div className="schema-form-widget-input-message">
          {renderProps['patternMessage']}
        </div>
      )}
    </div>
  );
};
