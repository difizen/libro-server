import { PageConfig, ServerConnection, ServerManager } from '@difizen/libro-jupyter';
import { ConfigurationService } from '@difizen/mana-app';
import { SlotViewManager } from '@difizen/mana-app';
import { ApplicationContribution, ViewManager } from '@difizen/mana-app';
import { inject, singleton } from '@difizen/mana-app';

@singleton({ contrib: ApplicationContribution })
export class LibroApp implements ApplicationContribution {
  @inject(ServerConnection) serverConnection: ServerConnection;
  @inject(ServerManager) serverManager: ServerManager;
  @inject(ViewManager) viewManager: ViewManager;
  @inject(SlotViewManager) slotViewManager: SlotViewManager;
  @inject(ConfigurationService) configurationService: ConfigurationService;

  async onStart() {
    let baseUrl = PageConfig.getOption('baseUrl');
    const el = document.getElementById('jupyter-config-data');
    if (el) {
      const pageConfig = JSON.parse(el.textContent || '') as Record<string, string>;
      baseUrl = pageConfig['baseUrl'];
      if (baseUrl && baseUrl.startsWith('/')) {
        baseUrl = window.location.origin + baseUrl;
      }
    }
    this.serverConnection.updateSettings({
      baseUrl,
      wsUrl: baseUrl.replace(/^http(s)?/, 'ws$1'),
    });
    this.serverManager.launch();
  }
}
