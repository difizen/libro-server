import { LibroJupyterModule } from '@difizen/libro-jupyter';
import { createSlotPreference, ManaAppPreset, ManaComponents, ManaModule, RootSlotId } from '@difizen/mana-app';
import React from 'react';
import { LibroApp } from './app.js';
import './index.less';
import { LibroInterpreterView } from './libro-interpreter-view.js';

const BaseModule = ManaModule.create().register(LibroApp,LibroInterpreterView,
    createSlotPreference({
        slot: RootSlotId,
        view: LibroInterpreterView,
    })
);

const App = (): JSX.Element => {
  return (
    <div className="libro-interpreter-container">
      <ManaComponents.Application
        key="libro"
        asChild={true}
        modules={[
          ManaAppPreset,
          LibroJupyterModule,
          BaseModule
        ]}
      />
    </div>
  );
};

export default App;
