import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";

import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

const vuetify = createVuetify({
    components,
    directives,
    theme: {
        defaultTheme: "light",
        themes: {
            light: {
                colors: {
                    primary: "#00BCD4",
                    secondary: "#26C6DA",
                    background: "#F8FAFC",
                    surface: "#FFFFFF",
                },
            },
        },
    },
});

createApp(App)
    .use(router)
    .use(vuetify)
    .mount("#app");
