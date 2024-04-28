export default [
  {
    path: '/lab/execution',
    component: 'execution',
  },
  {
    path: '/libro/execution',
    component: 'execution',
  },
  {
    path: '/lab',
    component: 'libro',
  },
  {
    path: '/libro',
    component: 'libro',
  },
  {
    path: '/',
    component: 'libro',
    routes: [],
  },
];
