import { BaseView, ViewManager, ViewRender, singleton, useInject, view } from "@difizen/mana-app";
import { memo, useEffect, useState } from "react";
import { LibroHackthonView } from "./libro-hackthon-view.js";
import qs from 'query-string';

export const DemoHackthonComponent = memo(function LibroAppComponent() {
    const viewManager = useInject<ViewManager>(ViewManager);
    const [libroHackthonView,setLibroHackthonView] = useState<LibroHackthonView>();
    useEffect(()=>{
        const queryParams = qs.parse(window.location.search);
        console.log("🚀 ~ useEffect ~ queryParams:", queryParams)
        const filePath = queryParams['path'];
        viewManager.getOrCreateView(LibroHackthonView,{
            resource: filePath,
        }).then((view)=>{
            setLibroHackthonView(view);
        })
    },[])
  
    return (
      <div
        className="demo-hackthon"
      >
        {libroHackthonView&&<ViewRender view={libroHackthonView}></ViewRender>}
      </div>
    );
});

@singleton()
@view('demo-hackthon')
export class DemoHackthonView extends BaseView {
  override view = DemoHackthonComponent;
}