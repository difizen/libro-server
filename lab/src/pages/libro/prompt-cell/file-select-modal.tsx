import { ModalItemProps, ModalItem, FileStat, ModalService } from '@difizen/mana-app';
import { CommandRegistry } from '@difizen/mana-app';
import { URI, useInject, ViewManager } from '@difizen/mana-app';
import { Col, Form, message, Row, Input, Modal, List, Button } from 'antd';
import type { InputRef } from 'antd';
import { useEffect, useRef, useState } from 'react';
import { CellView, JupyterFileService } from '@difizen/libro-jupyter';
import React from 'react';
import { FileImageOutlined, FileJpgOutlined, FilePdfOutlined } from '@ant-design/icons';
import { LibroFinPromptCellView } from './prompt-cell-view.js';

export interface ModalItemType {
  fileTypes?: FileType[];
  cell: CellView;
}

type FileType = '.ipynb' | '.py' | '.json' | '.sql' | undefined;

export const FileSelectModalComponent: React.FC<ModalItemProps<ModalItemType>> = ({
  visible,
  close,
  data,
}: ModalItemProps<ModalItemType>) => {
  const fileService = useInject(JupyterFileService);
  const modal = useInject(ModalService);

  const [fileList, setFileList] = useState<FileStat[]>([]);

  useEffect(() => {
    fileService.resolve(new URI('/')).then((res) => {
      if (res && res.children) {
        const files = res.children.filter((item) => {
          const path = item.resource.path.toString();
          const path_lower = path.toLowerCase();
          if (
            path_lower.endsWith('.pdf') ||
            path_lower.endsWith('.jpg') ||
            path_lower.endsWith('.jpeg') ||
            path_lower.endsWith('.png')
          ) {
            return true;
          }
        });
        setFileList(files);
      }
    });
  }, []);

  const renderAvatar = (item: FileStat) => {
    const path = item.resource.path.toString();
    if (path.endsWith('pdf')) return <FilePdfOutlined />;
    if (path.endsWith('jpg')) return <FileJpgOutlined />;
    if (path.endsWith('jpeg')) return <FileJpgOutlined />;
    if (path.endsWith('png')) return <FileImageOutlined />;
  };

  const onSelect = async (item: FileStat) => {
    if (data && data.cell) {
      const cell = data.cell;
      if (cell instanceof LibroFinPromptCellView) {
        const filename = item.resource.path.base;
        await cell.putFile(filename);
      }
    }
    modal.closeModal(FileSelectModal);
  };

  return (
    <Modal
      title="选择文件"
      open={visible}
      onCancel={close}
      width={788}
      keyboard={true}
      footer={null}
      wrapClassName="libro-create-file-modal"
    >
      <List
        itemLayout="horizontal"
        dataSource={fileList}
        renderItem={(item, index) => (
          <List.Item
            key={item.resource.path.toString()}
            actions={[<Button onClick={() => onSelect(item)}>选择</Button>]}
          >
            <List.Item.Meta
              avatar={renderAvatar(item)}
              title={item.resource.path.base}
            />
          </List.Item>
        )}
      />
    </Modal>
  );
};

export const FileSelectModal: ModalItem<ModalItemType> = {
  id: 'file.select.modal',
  component: FileSelectModalComponent,
};
