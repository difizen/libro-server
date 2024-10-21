import type { LibroModel } from '@difizen/libro-core';
import {
  LibroCommandRegister,
  LibroService,
  LibroToolbarArea,
  LibroView,
} from '@difizen/libro-core';
import { LibroCellModel, ServerConnection } from '@difizen/libro-jupyter';
import axios from 'axios';
import type { CommandRegistry, ToolbarRegistry } from '@difizen/mana-app';
import {
  CommandContribution,
  inject,
  ModalService,
  singleton,
  ToolbarContribution,
} from '@difizen/mana-app';
import { LibroTestCommand } from './test-command.js';
import { ShrinkOutlined } from '@ant-design/icons';
import React from 'react';
import { EventSourceParserStream, ParsedEvent } from 'eventsource-parser/stream';

@singleton({ contrib: [CommandContribution,ToolbarContribution] })
export class LibroTestCommandContribution implements CommandContribution,ToolbarContribution {
  @inject(ModalService) protected readonly modalService: ModalService;
  @inject(LibroCommandRegister) protected readonly libroCommand: LibroCommandRegister;
  @inject(LibroService) protected readonly libroService: LibroService;
  @inject(ServerConnection) serverConnection: ServerConnection;

  protected handleChatEvent = (e: ParsedEvent | undefined) => {
    if (!e) {
      return;
    }
    try {
      const data = JSON.parse(e.data);
      // if (e.event === 'message') {
      //   const newMessageModel: ChatMessageModel = JSON.parse(e.data);
      //   const message = this.getOrCreateMessage(newMessageModel);
      //   this.messages = [...this.messages, message];
      //   setImmediate(() => this.scrollToBottom(true, false));
      // }

      if (e.event === 'result') {
        const result = data;
        console.log("🚀 ~ LibroTestCommandContribution ~ result:", result)
      }

      ai.handleEventData(e, data);
    } catch (e) {
      console.warn('[chat] recerved server send event', event);
      console.error(e);
    }
  };

  registerCommands(command: CommandRegistry): void {
    this.libroCommand.registerLibroCommand(
      command,
      LibroTestCommand['TestCommand'],
      {
        execute: async (cell, libro) => {
          const res = await axios.post(
            `${this.serverConnection.settings.baseUrl}libro/api/chat`,
            {
              chat_key:"LLM:gpt4",
              prompt: "你是谁？",
            },
          );
          try {
            const response = await axios.post<ReadableStream<Uint8Array>>(`${this.serverConnection.settings.baseUrl}libro/api/chatstream`,             {
              chat_key:"LLM:gpt4",
              prompt: "你是谁？",
            }, {
                headers: {
                    Accept: 'text/event-stream',
                },
                responseType: 'stream', // 配置为流式响应
                adapter: 'fetch',
            });
            const stream = response.data;
            const reader = stream
              .pipeThrough(new TextDecoderStream())
              .pipeThrough(new EventSourceParserStream())
              .getReader();

            // const reader = response.data.getReader();
            // const decoder = new TextDecoder('utf-8');
    
            // 处理 SSE 响应
            const chunks: string[] = [];
            while (true) {
                const { done, value } = await reader.read();
                console.log("🚀 ~ LibroTestCommandContribution ~ execute: ~ value:", value)
                if (done) break;
    
                // const chunk = decoder.decode(value, { stream: true });
                // console.log("🚀 ~ LibroTestCommandContribution ~ execute: ~ chunk:", chunk)
                // chunks.push(chunk);
    
                // 处理每一行数据
                // chunk.split('\n').forEach((line) => {
                //     if (line.startsWith('data:')) {
                //         const data = line.replace('data: ', '').trim();
                //         console.log('Received:', data);  // 处理数据
                //     }
                // });
            }
    
            return chunks.join(''); // 返回完整的响应
          } catch (error) {
            console.error('Error fetching response:', error);
            throw error;
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
      id: LibroTestCommand['TestCommand'].id,
      icon: ShrinkOutlined,
      command: LibroTestCommand['TestCommand'].id,
    });
  }
}
