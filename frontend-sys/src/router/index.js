import { createRouter, createWebHistory } from "vue-router";
import CocinaView from "../views/CocinaView.vue";
import CamareroView from "../views/CamareroView.vue";
import CajaView from "../views/CajaView.vue";
import PedidosView from "../views/PedidosView.vue";
import GerenciaView from "../views/GerenciaView.vue";

const routes = [
  {
    path: "/",
    redirect: "/cocina",
  },
  {
    path: "/cocina",
    name: "cocina",
    component: CocinaView,
  },
  {
    path: "/camarero",
    name: "camarero",
    component: CamareroView,
  },
  {
    path: "/caja",
    name: "caja",
    component: CajaView,
  },
  {
    path: "/pedidos",
    name: "pedidos",
    component: PedidosView,
  },
  {
    path: "/gerencia",
    name: "gerencia",
    component: GerenciaView,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
