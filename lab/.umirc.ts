import { defineConfig } from 'umi';

export default defineConfig({
  publicPath: '/',
  routes: [{ path: '/*', component: 'libro' }],
  runtimePublicPath: {},
  proxy: {
    '/api': {
      target: 'http://localhost:8888/',

      changeOrigin: true,
      secure: false,
      pathRewrite: {},
      ws: true,
    },
    '/lsp': {
      target: 'http://localhost:8888/',
      changeOrigin: true,
      secure: false,
      ws: true,
    },
  },
  extraBabelPlugins: [
    ['@babel/plugin-proposal-decorators', { legacy: true }],
    ['@babel/plugin-transform-flow-strip-types', { allowDeclareFields: true }],
    ['@babel/plugin-transform-private-methods', { loose: true }],
    ['@babel/plugin-transform-private-property-in-object', { loose: true }],
    ['@babel/plugin-transform-class-properties', { loose: true }],
    'babel-plugin-parameter-decorator',
  ],
  plugins: ['./dumi-plugin-nodenext'],
  mfsu: false,
  jsMinifier: 'none',
});
