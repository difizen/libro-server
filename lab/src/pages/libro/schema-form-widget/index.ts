import { ManaModule } from '@difizen/mana-app';
import { WidgetModule } from '@difizen/libro-widget';
import { SchemaFormModelContribution } from './contribution.js';
import { LibroSchemaFormtWidget } from './view.js';

export const LibroSchemaFormWidgetModule = ManaModule.create()
  .register(LibroSchemaFormtWidget, SchemaFormModelContribution)
  .dependOn(WidgetModule);
