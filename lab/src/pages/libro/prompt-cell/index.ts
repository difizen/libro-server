import { ManaModule, Syringe } from '@difizen/mana-app';
import { PromptScript, LibroPromptCellModel } from '@difizen/libro-prompt-cell';
import { LibroPromptScript } from './prompt-script.js';
import { LibroFinPromptCellView } from './prompt-cell-view.js';
import { FinLibroPromptCellModel } from './prompt-cell-model.js';
import { FinFormatterPromptMagicContribution } from './libro-formatter-prompt-magic-contribution.js';
import { FinLibroPromptOutputMimeTypeContribution } from './prompt-output-rendermime-contribution.js';
import { PromptHelper } from './prompt-helper.js';
import { FileSelectModalContribution } from './file-select-modal-contribution.js';

export const FinPromptCellModule = ManaModule.create().register(
  LibroFinPromptCellView,
  FinFormatterPromptMagicContribution,
  FinLibroPromptOutputMimeTypeContribution,
  FileSelectModalContribution,
  PromptHelper,
  {
    token: LibroPromptCellModel,
    useClass: FinLibroPromptCellModel,
  },
  {
    token: PromptScript,
    useClass: LibroPromptScript,
    lifecycle: Syringe.Lifecycle.singleton,
  },
);
