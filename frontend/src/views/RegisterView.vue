<template>
    <v-container class="page-wrapper" fluid>
        <v-card class="register-card" elevation="8">
            <v-card-title class="text-h5 font-weight-bold text-center">
                Proxy Access Service
            </v-card-title>

            <v-card-subtitle class="text-center mb-4">
                Регистрация и получение ключа доступа
            </v-card-subtitle>

            <v-form @submit.prevent="register">
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
                    :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    @click:append-inner="showPassword = !showPassword"
                />

                <v-text-field
                    v-model="form.password_confirm"
                    :type="showPasswordConfirm ? 'text' : 'password'"
                    label="Подтверждение пароля"
                    variant="outlined"
                    color="primary"
                    prepend-inner-icon="mdi-lock-check"
                    :append-inner-icon="showPasswordConfirm ? 'mdi-eye-off' : 'mdi-eye'"
                    @click:append-inner="showPasswordConfirm = !showPasswordConfirm"
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
                    Зарегистрироваться
                </v-btn>
            </v-form>

            <div class="text-center mt-4">
                <span>Уже есть аккаунт?</span>
                <router-link to="/login" class="login-link">
                    Войти
                </router-link>
            </div>
        </v-card>
    </v-container>
</template>

<script setup>
import { reactive, ref } from "vue";

import apiClient from "../api/client";

const form = reactive({
    email: "",
    password: "",
    password_confirm: "",
});

const loading = ref(false);
const message = ref("");
const error = ref("");
const showPassword = ref(false);
const showPasswordConfirm = ref(false);

async function register() {
    loading.value = true;
    message.value = "";
    error.value = "";

    try {
        const response = await apiClient.post(
            "/register/",
            form,
        );

        message.value = response.data.message;

        form.email = "";
        form.password = "";
        form.password_confirm = "";
    } catch (err) {
        error.value =
            err.response?.data?.detail ||
            "Ошибка регистрации. Проверьте данные.";
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

.register-card {
    width: 100%;
    max-width: 460px;
    padding: 28px;
    border-radius: 24px;
}

.login-link {
    margin-left: 6px;
    color: #00bcd4;
    font-weight: 600;
    text-decoration: none;
}

.login-link:hover {
    text-decoration: underline;
}
</style>
