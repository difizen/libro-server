import { ModalContribution, singleton } from '@difizen/mana-app';

import { FileSelectModal } from './file-select-modal.js';

@singleton({ contrib: ModalContribution })
export class FileSelectModalContribution implements ModalContribution {
  registerModal() {
    return FileSelectModal;
  }
}
