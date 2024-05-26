import { LibroLabModule } from '@difizen/libro-lab';
import { ManaAppPreset, ManaComponents, ManaModule } from '@difizen/mana-app';

import { LibroApp } from './app.js';
import './index.less';
import { LibroSchemaFormWidgetModule } from './schema-form-widget/index.js';
import { FinPromptCellModule } from './prompt-cell/index.js';
import { LibroBetweenCellModule } from '@difizen/libro-jupyter';
import { ProgressWidget, ProgressWidgetViewContribution } from './progress/index.js';
import { LibroWidgetMimeContribution } from './widget-rendermime-contribution.js';

const BaseModule = ManaModule.create()
  .register(
    LibroApp,
    ProgressWidgetViewContribution,
    ProgressWidget,
    LibroWidgetMimeContribution,
  )
  .dependOn(FinPromptCellModule, LibroLabModule);

const App = (): JSX.Element => {
  return (
    <div className="libro-workbench-app">
      <ManaComponents.Application
        key="libro"
        asChild={true}
        modules={[
          ManaAppPreset,
          LibroLabModule,
          BaseModule,
          LibroSchemaFormWidgetModule,
          LibroBetweenCellModule,
        ]}
      />
    </div>
  );
};

export default App;
