import { createRouter, createWebHistory } from "vue-router";

import RegisterView from "../views/RegisterView.vue";
import LoginView from "../views/LoginView.vue";
import ProfileView from "../views/ProfileView.vue";

const routes = [
    {
        path: "/",
        redirect: "/register",
    },
    {
        path: "/register",
        name: "register",
        component: RegisterView,
    },
    {
        path: "/login",
        name: "login",
        component: LoginView,
    },
    {
        path: "/profile",
        name: "profile",
        component: ProfileView,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
