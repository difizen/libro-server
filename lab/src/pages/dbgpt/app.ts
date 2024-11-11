import {
  FileCommandContribution,
  LibroFileService,
  LibroJupyterConfiguration,
  PageConfig,
  ServerConnection,
  ServerManager,
} from '@difizen/libro-jupyter';
import { ConfigurationService, FileTreeView, FileTreeViewFactory, OpenerService, URI } from '@difizen/mana-app';
import { SlotViewManager } from '@difizen/mana-app';
import { terminalDefaultSlot } from '@difizen/libro-terminal';
import qs from 'query-string';
import { ApplicationContribution, ViewManager } from '@difizen/mana-app';
import { inject, singleton } from '@difizen/mana-app';
import { Fetcher } from '@difizen/magent-core';
import { LayoutService, LibroLabLayoutSlots } from '@difizen/libro-lab';
const ShouldPreventStoreViewKey = 'mana-should-prevent-store-view';

@singleton({ contrib: ApplicationContribution })
export class LibroApp implements ApplicationContribution {
  @inject(ServerConnection) serverConnection: ServerConnection;
  @inject(ServerManager) serverManager: ServerManager;
  @inject(ViewManager) viewManager: ViewManager;
  @inject(SlotViewManager) slotViewManager: SlotViewManager;
  @inject(ConfigurationService) configurationService: ConfigurationService;
  @inject(LayoutService) layoutService: LayoutService;
  @inject(FileCommandContribution) fileCommandContribution: FileCommandContribution;
  @inject(Fetcher) fetcher: Fetcher;
  @inject(OpenerService) openerService: OpenerService;
  @inject(LibroFileService) libroFileService: LibroFileService;
  location: string

  async onStart() {
    this.configurationService.set(LibroJupyterConfiguration.AllowDownload, true);
    this.configurationService.set(LibroJupyterConfiguration.AllowUpload, true);
    this.fileCommandContribution.allowUpload = true;
    this.fileCommandContribution.allowDownload = true;
    let baseUrl = PageConfig.getOption('baseUrl');
    const el = document.getElementById('jupyter-config-data');
    if (el) {
      const pageConfig = JSON.parse(el.textContent || '') as Record<string, string>;
      baseUrl = pageConfig['baseUrl'];
      if (baseUrl && baseUrl.startsWith('/')) {
        baseUrl = window.location.origin + baseUrl;
      }
    }
    localStorage.setItem(ShouldPreventStoreViewKey, 'true');
    this.configurationService.set(
      LibroJupyterConfiguration['OpenSlot'],
      LibroLabLayoutSlots.content,
    );
    this.configurationService.set(
      terminalDefaultSlot,
      LibroLabLayoutSlots.contentBottom,
    );
    this.serverConnection.updateSettings({
      baseUrl,
      wsUrl: baseUrl.replace(/^http(s)?/, 'ws$1'),
    });
    this.serverManager.launch();
    this.serverManager.ready
      .then(async () => {
        this.layoutService.setAreaVisible(LibroLabLayoutSlots.navigator, true);
        this.layoutService.setAreaVisible(LibroLabLayoutSlots.alert, false);
        this.layoutService.serverSatus = 'success';
        await this.initialWorkspace();
        if(this.location){
          const defaultOpenUri = new URI(this.location+'/__init__.py');

          this.openerService.getOpener(defaultOpenUri).then((opener) => {
            if (opener) {
              opener.open(defaultOpenUri, {
                viewOptions: {
                  name: '__init__.py',
                },
              });
            }
          });
        }
        return;
      })
      .catch(console.error);
  }

  protected async initialWorkspace() {    
    const queryParams = qs.parse(window.location.search);
    const flow_uid = queryParams['flow_uid'];
    const res = await this.fetcher.get<any>(`/api/v1/serve/awel/flow/notebook/file/path`, {
      flow_uid:flow_uid,
    },{baseURL:'http://localhost:5670'});
    if(res.status&& res.data?.data?.path){
      const view =
      await this.viewManager.getOrCreateView<FileTreeView>(FileTreeViewFactory);
      if (view) {
        const location = res.data?.data?.path;
        this.location = location;
        view.model.rootVisible = false;
        view.model.location = new URI(location);
      }
    }
  }
}
