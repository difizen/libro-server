import { LibroLabApp, LibroLabCurrentFileFooterView, LibroLabLayoutView, LibroLabModule } from '@difizen/libro-lab';
import { ManaAppPreset, ManaComponents, ManaModule, Syringe } from '@difizen/mana-app';

import { LibroApp } from './app.js';
import './index.less';
import { LibroPromptScript } from './prompt-script.js';
import { PromptScript } from '@difizen/libro-prompt-cell';
import { LibroSchemaFormWidgetModule } from './schema-form-widget/index.js';
import { LibroDbgptLayoutView } from './dbgbt-layout.js'
import { LibroDbgptLabCurrentFileFooterView } from './dbgpt-current-file-footer-view.js'

const BaseModule = ManaModule.create().register({
  token:LibroLabApp,
  useClass:LibroApp
},
  {
    token: PromptScript,
    useClass: LibroPromptScript,
    lifecycle: Syringe.Lifecycle.singleton,
  },
  {
    token:LibroLabLayoutView,
    useClass:LibroDbgptLayoutView
  },
  {
    token:LibroLabCurrentFileFooterView,
    useClass:LibroDbgptLabCurrentFileFooterView
  }
);

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
        ]}
      />
    </div>
  );
};

export default App;
