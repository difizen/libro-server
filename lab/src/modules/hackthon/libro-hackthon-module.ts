import { ManaModule } from "@difizen/mana-app";
import { LibroHackthonCommandContribution } from "./libro-hackthon-command-contribution.js";
import { LibroHackthonView } from "./libro-hackthon-view.js";
import { LibroHackthonChatbotView } from "./libro-hackthon-chatbot-view.js";

export const LibroHackthonModule = ManaModule.create().register(LibroHackthonChatbotView,LibroHackthonView,LibroHackthonCommandContribution)