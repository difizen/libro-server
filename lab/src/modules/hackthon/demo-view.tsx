import { BaseView, ViewManager, ViewRender, singleton, useInject, view } from "@difizen/mana-app";
import { memo, useEffect, useState } from "react";
import { LibroHackthonView } from "./libro-hackthon-view.js";
import qs from 'query-string';
import { LibroHackthonChatbotView } from "./libro-hackthon-chatbot-view.js";

export const DemoHackthonComponent = memo(function LibroAppComponent() {
    const viewManager = useInject<ViewManager>(ViewManager);
    const [libroHackthonView,setLibroHackthonView] = useState<LibroHackthonView>();
    const [hackthonChatbotView,setHackthonChatbotView] = useState<LibroHackthonChatbotView>();
    useEffect(()=>{
        const queryParams = qs.parse(window.location.search);
        console.log("🚀 ~ useEffect ~ queryParams:", queryParams)
        const filePath = queryParams['path'];
        viewManager.getOrCreateView(LibroHackthonView,{
            resource: filePath,
        }).then((view)=>{
            setLibroHackthonView(view);
        })
        viewManager.getOrCreateView(LibroHackthonChatbotView).then((view)=>{
          setHackthonChatbotView(view);
        })
    },[])
  
    return (
      <div
        className="demo-hackthon"
      >
        {hackthonChatbotView&&<ViewRender view={hackthonChatbotView}></ViewRender>}
        {libroHackthonView&&<ViewRender view={libroHackthonView}></ViewRender>}
      </div>
    );
});

@singleton()
@view('demo-hackthon')
export class DemoHackthonView extends BaseView {
  override view = DemoHackthonComponent;
}