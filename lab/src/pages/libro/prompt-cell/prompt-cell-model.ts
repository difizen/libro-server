import type { ICodeCellMetadata } from '@difizen/libro-common';
import type { ICodeCell } from '@difizen/libro-common';
import type { ExecutionMeta } from '@difizen/libro-jupyter';
import { inject, transient } from '@difizen/mana-app';
import { prop } from '@difizen/mana-app';
import { LibroPromptCellModel } from '@difizen/libro-prompt-cell';

export interface PromptCellMetadata extends ICodeCellMetadata {
  execution: ExecutionMeta;
}

@transient()
export class FinLibroPromptCellModel extends LibroPromptCellModel {
  @prop()
  filename?: string;

  override get decodeObject() {
    return {
      ...this._decodeObject,
      variableName: this.variableName,
      chatKey: this.chatKey,
      record: this.record,
      value: this.value,
      cellId: this.id,
      filename: this.filename,
    };
  }

  override set decodeObject(value) {
    super.decodeObject = value;
    this.variableName = value.variableName;
    this.chatKey = value.chatKey;
    this.record = value.record;
    this.filename = value.filename;
  }

  override toJSON(): Omit<ICodeCell, 'outputs'> {
    return {
      id: this.id,
      cell_type: this.type,
      source: this.source,
      metadata: this.metadata,
      execution_count: this.executeCount,
      // outputs: this.outputs,
    };
  }

  override dispose() {
    super.dispose();
    this.msgChangeEmitter.dispose();
  }
}
