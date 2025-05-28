import { createRouter, createWebHistory } from 'vue-router'
import Configurator from './components/Configurator.vue'
import AdminView from './components/AdminView.vue'

const routes = [
  { path: '/', component: Configurator },
  { path: '/admin', component: AdminView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router