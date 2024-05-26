import { prop, singleton } from '@difizen/mana-app';

@singleton()
export class PromptHelper {
  @prop()
  latestRecord?: string;
}
