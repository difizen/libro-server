import * as path from 'path';
function initPublicPath() {
  const url = new URL((document.currentScript as HTMLScriptElement).src);
  const cdn = url.origin + path.join(url.pathname, '../');
  window.__webpack_public_path__ = cdn;
}

initPublicPath();
