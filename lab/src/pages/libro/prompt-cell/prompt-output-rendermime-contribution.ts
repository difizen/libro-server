import type { BaseOutputView } from '@difizen/libro-jupyter';
import { RenderMimeContribution } from '@difizen/libro-jupyter';
import { singleton } from '@difizen/mana-app';

import { PromptOutputRender } from './prompt-output-render.js';

@singleton({ contrib: RenderMimeContribution })
export class FinLibroPromptOutputMimeTypeContribution
  implements RenderMimeContribution
{
  canHandle = (model: BaseOutputView) => {
    return 400;
  };
  renderType = 'promptOutputRender';
  safe = true;
  mimeTypes = ['application/vnd.libro.prompt+json'];
  render = PromptOutputRender;
}
