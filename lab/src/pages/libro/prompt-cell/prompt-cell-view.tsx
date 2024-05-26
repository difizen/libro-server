import {
  getOrigin,
  inject,
  ModalService,
  prop,
  transient,
  useInject,
  view,
  ViewInstance,
  ViewRender,
} from '@difizen/mana-app';
import { Select, Tag, Upload, Button, message } from 'antd';
import classNames from 'classnames';
import React, { useEffect, useState } from 'react';
import { LibroPromptCellView } from '@difizen/libro-prompt-cell';
import { VariableNameInput, ChatRecordInput } from './input-handler/index.js';
import './index.less';
import { EllipsisOutlined, UploadOutlined } from '@ant-design/icons';
import { DragAreaKey, ServerConnection } from '@difizen/libro-jupyter';
import { FinLibroPromptCellModel } from './prompt-cell-model.js';
import { PromptHelper } from './prompt-helper.js';
import classnames from 'classnames';
import { FileSelectModal } from './file-select-modal.js';

export interface ChatObject {
  name: string;
  type: string;
  order: number;
  key: string;
  disabled?: boolean;
}
export interface ChatObjectOptions {
  order?: number;
  color?: string;
}

const ChatObjectOptions = (type: string): ChatObjectOptions => {
  switch (type) {
    case 'LLM':
      return {
        order: 1,
        color: 'blue',
      };
    case 'LMM':
      return {
        order: 2,
        color: 'cyan',
      };
    case 'VARIABLE':
      return {
        order: 3,
        color: 'red',
      };
    case 'API':
      return {
        order: 4,
        color: 'green',
      };
    case 'CUSTOM':
      return {
        order: 5,
        color: undefined,
      };
    default:
      return {
        order: undefined,
        color: undefined,
      };
  }
};

const SelectionItemLabel: React.FC<{ item: ChatObject }> = (props: {
  item: ChatObject;
}) => {
  const item = props.item;

  return (
    <span
      className={classNames('libro-prompt-cell-selection', {
        'libro-prompt-cell-selection-disabled': item.disabled,
      })}
    >
      <Tag
        color={ChatObjectOptions(item.type).color}
        className="libro-prompt-cell-selection-tag"
      >
        {item.type}
      </Tag>
      <span className="libro-prompt-cell-selection-name">{item.name}</span>
    </span>
  );
};
const CellEditorRaw: React.FC = () => {
  const instance = useInject<LibroPromptCellView>(ViewInstance);
  useEffect(() => {
    if (instance.editorView?.editor) {
      instance.editor = getOrigin(instance.editorView?.editor);
    }
  }, [instance, instance.editorView?.editor]);
  return <>{instance.editorView && <ViewRender view={instance.editorView} />}</>;
};

export const CellEditor = React.memo(CellEditorRaw);

const PropmtEditorViewComponent = React.forwardRef<HTMLDivElement>(
  function PropmtEditorViewComponent(props, ref) {
    const instance = useInject<LibroFinPromptCellView>(ViewInstance);
    const modal = useInject<ModalService>(ModalService);
    const [selectedModel, setSelectedModel] = useState<string>('暂无内置模型');
    const [isDragOver, setIsDragOver] = useState<boolean>(false);
    useEffect(() => {
      // TODO: Data initialization should not depend on view initialization, which causes limitations in usage scenarios and multiple renderings.
      instance.model.variableName = instance.model.decodeObject.variableName;
      instance
        .updateChatObjects()
        .then(() => {
          const len = instance.chatObjects.length;
          if (len > 0) {
            if (!instance.model.decodeObject.chatKey) {
              instance.model.chatKey = instance.chatObjects[len - 1].key;
            } else {
              instance.model.chatKey = instance.model.decodeObject.chatKey;
            }
            setSelectedModel(instance.model.chatKey);
            return;
          }
          return;
        })
        .catch(() => {
          //
        });
      instance.updateChatRecords();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleChange = (value: string) => {
      instance.handleModelNameChange(value);
      setSelectedModel(value);
    };

    return (
      <div
        className={instance.className}
        ref={ref}
        tabIndex={10}
        onBlur={instance.blur}
      >
        <div className="libro-prompt-cell-header">
          <div>
            <span>
              <Select
                value={selectedModel}
                style={{ minWidth: 160 }}
                onChange={handleChange}
                options={instance.sortedChatObjects.map(instance.toSelectionOption)}
                bordered={false}
                onFocus={async () => {
                  await instance.updateChatObjects();
                }}
              />
            </span>
            <VariableNameInput
              value={instance.model.variableName}
              checkVariableNameAvailable={instance.checkVariableNameAvailable}
              handleVariableNameChange={instance.handleVariableNameChange}
            />
          </div>
          <div>
            <ChatRecordInput
              value={instance.model.record}
              handleChange={instance.handleRecordChange}
              records={instance.chatRecords}
              onFocus={instance.updateChatRecords}
            />
          </div>
        </div>
        <CellEditor />
        <div
          className={classnames('libro-prompt-cell-upload-area', {
            ['libro-prompt-cell-upload-area-drag-over']: isDragOver,
          })}
          draggable={true}
          onDragOver={(e) => {
            setIsDragOver(true);
          }}
          onDragLeave={(e) => {
            setIsDragOver(false);
          }}
          onDrop={(e) => {
            console.log(e);
          }}
          onDragEnd={(e) => {
            console.log(e);
          }}
        >
          <Upload
            rootClassName="libro-prompt-cell-upload-wrapper"
            className="libro-prompt-cell-upload"
            fileList={instance.fileList}
            name="file"
            action={`${instance.serverConnection.settings.baseUrl}libro/api/upload`}
            headers={{
              authorization: 'authorization-text',
            }}
            onRemove={() => {
              instance.fileList = [];
              instance.model.filename = undefined;
            }}
            onChange={(info) => {
              if (info.file.status === 'uploading') {
                instance.fileList = [info.file];
                instance.model.filename = undefined;
              } else {
                //
              }
              if (info.file.status === 'done') {
                instance.fileList = [info.file];
                instance.model.filename = info.file.name;
                message.success(`${info.file.name} 文件上传成功。`);
              } else if (info.file.status === 'error') {
                instance.fileList = [info.file];
                instance.model.filename = undefined;
                message.error(`${info.file.name} 文件上传失败。`);
              }
            }}
          >
            <Button
              className="libro-prompt-cell-upload-selection"
              onClick={(e) => {
                e.stopPropagation();
                modal.openModal(FileSelectModal, { cell: instance });
              }}
              icon={<EllipsisOutlined />}
            >
              选择
            </Button>
            <Button icon={<UploadOutlined />}>上传</Button>
          </Upload>
        </div>
      </div>
    );
  },
);

@transient()
@view('prompt-editor-cell-view')
export class LibroFinPromptCellView extends LibroPromptCellView {
  declare model: FinLibroPromptCellModel;
  @inject(ServerConnection) serverConnection: ServerConnection;
  @inject(PromptHelper) helper: PromptHelper;
  @prop()
  protected _fileList: any[] = [];

  get fileList() {
    if (this.model.filename && this._fileList.length === 0) {
      return [
        {
          name: this.model.filename,
          status: 'done',
        },
      ];
    }
    return this._fileList;
  }
  set fileList(v) {
    this._fileList = v;
  }

  override view = PropmtEditorViewComponent;

  override onViewMount() {
    super.onViewMount();
    if (!this.model.record && this.helper.latestRecord) {
      this.model.record = this.helper.latestRecord;
    }
    if (!this.model.record) {
      this.model.record = 'default';
    }
  }

  putFile = async (name: string) => {
    const res = await this.serverConnection.makeRequest(
      `${this.serverConnection.settings.baseUrl}libro/api/upload`,
      {
        method: 'PUT',
        body: JSON.stringify({ filename: name }),
      },
    );
    const result = await res.json();
    this.model.filename = result.filename;
    this.fileList = [];
  };
}
