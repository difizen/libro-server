import { CheckSquareOutlined } from '@ant-design/icons';
import type { LibroModel } from '@difizen/libro-core';
import {
  LibroCommandRegister,
  LibroService,
  LibroToolbarArea,
  LibroView,
} from '@difizen/libro-core';
import { LibroCellModel } from '@difizen/libro-jupyter';
import type { CommandRegistry, ToolbarRegistry } from '@difizen/mana-app';
import {
  CommandContribution,
  inject,
  ModalService,
  singleton,
  ToolbarContribution,
} from '@difizen/mana-app';

export const LibroHackthonCommand = {
    RenderCellOutput: {
      id: 'libro-hackthon:render-cell-output',
      icon:<CheckSquareOutlined />
    },
    RenderLibro: {
        id: 'libro-hackthon:render-libro',
        icon:<CheckSquareOutlined />
    },
  };

@singleton({ contrib: [CommandContribution,ToolbarContribution] })
export class LibroHackthonCommandContribution implements CommandContribution,ToolbarContribution {
  @inject(ModalService) protected readonly modalService: ModalService;
  @inject(LibroCommandRegister) protected readonly libroCommand: LibroCommandRegister;
  @inject(LibroService) protected readonly libroService: LibroService;

  registerCommands(command: CommandRegistry): void {
    this.libroCommand.registerLibroCommand(
      command,
      LibroHackthonCommand['RenderCellOutput'],
      {
        execute: async (cell, libro) => {
          if (cell) {
            (cell.model as LibroCellModel).metadata = {...cell?.model.metadata,renderCellOutput:true}
          }
        },
        isVisible: (cell, libro, path) => {
          if (!libro || !(libro instanceof LibroView)) {
            return false;
          }
          return (
            path === LibroToolbarArea.CellRight
          );
        },
      },
    );

    this.libroCommand.registerLibroCommand(
      command,
      LibroHackthonCommand['RenderLibro'],
      {
        execute: (cell, libro) => {
          if(libro){
            (libro.model as LibroModel).metadata = {...libro?.model.metadata,renderLibro:true}
          }
        },
        isVisible: (cell, libro, path) => {
            if (!libro || !(libro instanceof LibroView)) {
              return false;
            }
            return (
              path === LibroToolbarArea.HeaderCenter
            );
          },
      },
    );
  }

  registerToolbarItems(registry: ToolbarRegistry): void {
    registry.registerItem({
      id:       LibroHackthonCommand['RenderCellOutput'].id,
      icon: LibroHackthonCommand['RenderCellOutput'].icon,
      command: LibroHackthonCommand['RenderCellOutput'].id,
    });
    registry.registerItem({
      id:       LibroHackthonCommand['RenderLibro'].id,
      icon: LibroHackthonCommand['RenderLibro'].icon,
      command: LibroHackthonCommand['RenderLibro'].id,
    });
  }
}
