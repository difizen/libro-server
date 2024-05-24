import { ManaAppPreset, ManaComponents, ManaModule, RootSlotId, createSlotPreference } from "@difizen/mana-app";
import { DemoHackthonView } from "../../modules/demo-view.js";
import { LibroJupyterModule } from "@difizen/libro-jupyter";
import { LibroHackthonModule } from "../../modules/libro-hackthon-module.js";

const BaseModule = ManaModule.create().register(
    DemoHackthonView,
    createSlotPreference({
        slot: RootSlotId,
        view: DemoHackthonView,
    }),
)
const LibroHackthon = (): JSX.Element => {
    return (
      <div className="libro-hackthon">
        <ManaComponents.Application
          key="libro-hackthon"
          asChild={true}
          modules={[ManaAppPreset, LibroHackthonModule,LibroJupyterModule, BaseModule]}
        />
      </div>
    );
  };
  
export default LibroHackthon;