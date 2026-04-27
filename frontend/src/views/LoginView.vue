<template>
    <v-container class="page-wrapper" fluid>
        <v-card class="login-card" elevation="8">
            <v-card-title class="text-h5 font-weight-bold text-center">
                Proxy Access Service
            </v-card-title>

            <v-card-subtitle class="text-center mb-4">
                Вход в личный кабинет
            </v-card-subtitle>

            <v-form @submit.prevent="loginUser">
                <v-text-field
                    v-model="form.email"
                    label="Email"
                    type="email"
                    variant="outlined"
                    color="primary"
                    prepend-inner-icon="mdi-email"
                />

                <v-text-field
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    label="Пароль"
                    variant="outlined"
                    color="primary"
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="
                        showPassword ? 'mdi-eye' : 'mdi-eye-off'
                    "
                    @click:append-inner="
                        showPassword = !showPassword
                    "
                />

                <v-alert
                    v-if="message"
                    type="success"
                    variant="tonal"
                    class="mb-4"
                >
                    {{ message }}
                </v-alert>

                <v-alert
                    v-if="error"
                    type="error"
                    variant="tonal"
                    class="mb-4"
                >
                    {{ error }}
                </v-alert>

                <v-btn
                    type="submit"
                    color="primary"
                    block
                    size="large"
                    :loading="loading"
                >
                    Войти
                </v-btn>
            </v-form>

            <div class="text-center mt-4">
                <span>Нет аккаунта?</span>
                <router-link to="/register" class="register-link">
                    Зарегистрироваться
                </router-link>
            </div>
        </v-card>
    </v-container>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import apiClient from "../api/client";

const router = useRouter();

const form = reactive({
    email: "",
    password: "",
});

const loading = ref(false);
const message = ref("");
const error = ref("");
const showPassword = ref(false);

async function loginUser() {
    loading.value = true;
    message.value = "";
    error.value = "";

    try {
        const response = await apiClient.post(
            "/login/",
            form,
        );

        message.value = response.data.message;

        setTimeout(() => {
            router.push("/profile");
        }, 500);
    } catch (err) {
        error.value =
            err.response?.data?.detail ||
            "Ошибка входа. Проверьте email и пароль.";
    } finally {
        loading.value = false;
    }
}
</script>

<style scoped>
.page-wrapper {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        radial-gradient(circle at top left, #ccfbf1 0, transparent 30%),
        linear-gradient(135deg, #f8fafc 0%, #ecfeff 100%);
}

.login-card {
    width: 100%;
    max-width: 460px;
    padding: 28px;
    border-radius: 24px;
}

.register-link {
    margin-left: 6px;
    color: #00bcd4;
    font-weight: 600;
    text-decoration: none;
}

.register-link:hover {
    text-decoration: underline;
}
</style>
