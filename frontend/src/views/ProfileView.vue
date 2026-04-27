<template>
    <v-container class="page-wrapper" fluid>
        <v-card class="profile-card" elevation="8">
            <v-card-title class="text-h5 font-weight-bold text-center">
                Личный кабинет
            </v-card-title>

            <v-card-subtitle class="text-center mb-6">
                Управление ключом доступа и паролем
            </v-card-subtitle>

            <v-alert v-if="message" type="success" variant="tonal" class="mb-4">
                {{ message }}
            </v-alert>

            <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
                {{ error }}
            </v-alert>

            <v-alert
                v-if="connectionStatus"
                :type="connectionStatusType"
                variant="tonal"
                class="mb-4"
            >
                {{ connectionStatus }}
            </v-alert>

            <v-list class="mb-4">
                <v-list-item>
                    <template #prepend>
                        <v-icon color="primary">mdi-email</v-icon>
                    </template>
                    <v-list-item-title>Email</v-list-item-title>
                    <v-list-item-subtitle>
                        {{ profile.email }}
                    </v-list-item-subtitle>
                </v-list-item>

                <v-list-item>
                    <template #prepend>
                        <v-icon color="primary">mdi-key</v-icon>
                    </template>
                    <v-list-item-title>Ключ активации</v-list-item-title>
                    <v-list-item-subtitle class="key-text">
                        {{ profile.activation_key || "Ключ отсутствует" }}
                    </v-list-item-subtitle>
                </v-list-item>

                <v-list-item>
                    <template #prepend>
                        <v-icon color="primary">mdi-check-circle</v-icon>
                    </template>
                    <v-list-item-title>Статус аккаунта</v-list-item-title>
                    <v-list-item-subtitle>
                        {{ profile.is_active ? "Активен" : "Не активен" }}
                    </v-list-item-subtitle>
                </v-list-item>

                <v-list-item>
                    <template #prepend>
                        <v-icon color="primary">mdi-lan-connect</v-icon>
                    </template>
                    <v-list-item-title>Статус подключения</v-list-item-title>
                    <v-list-item-subtitle>
                        {{ currentSocketStatus }}
                    </v-list-item-subtitle>
                </v-list-item>
            </v-list>

            <v-btn
                color="primary"
                block
                size="large"
                class="mb-3"
                :loading="refreshLoading"
                @click="refreshKey"
            >
                Обновить ключ
            </v-btn>

            <!-- СКРЫВАЕМ если уже подключен -->
            <v-btn
                v-if="socketStatus !== 'connected'"
                color="primary"
                variant="outlined"
                block
                size="large"
                class="mb-6"
                :loading="connectLoading"
                @click="connectProxy"
            >
                Подключиться к прокси
            </v-btn>

            <v-card v-if="proxy" class="proxy-card mb-6" elevation="0">
                <div class="text-subtitle-1 font-weight-bold mb-2">
                    Данные прокси
                </div>

                <div><strong>Host:</strong> {{ proxy.host }}</div>
                <div><strong>Port:</strong> {{ proxy.port }}</div>
                <div><strong>Protocol:</strong> {{ proxy.protocol }}</div>
            </v-card>

            <v-divider class="mb-6" />

            <div class="text-subtitle-1 font-weight-bold mb-3">
                Смена пароля
            </div>

            <v-form @submit.prevent="changePassword">
                <v-text-field
                    v-model="passwordForm.old_password"
                    :type="showOldPassword ? 'text' : 'password'"
                    label="Старый пароль"
                    variant="outlined"
                    color="primary"
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="showOldPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append-inner="showOldPassword = !showOldPassword"
                />

                <v-text-field
                    v-model="passwordForm.new_password"
                    :type="showNewPassword ? 'text' : 'password'"
                    label="Новый пароль"
                    variant="outlined"
                    color="primary"
                    prepend-inner-icon="mdi-lock-reset"
                    :append-inner-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append-inner="showNewPassword = !showNewPassword"
                />

                <v-text-field
                    v-model="passwordForm.new_password_confirm"
                    :type="showNewPasswordConfirm ? 'text' : 'password'"
                    label="Подтверждение нового пароля"
                    variant="outlined"
                    color="primary"
                    prepend-inner-icon="mdi-lock-check"
                    :append-inner-icon="showNewPasswordConfirm ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append-inner="showNewPasswordConfirm = !showNewPasswordConfirm"
                />

                <v-btn
                    type="submit"
                    color="primary"
                    variant="outlined"
                    block
                    size="large"
                    :loading="passwordLoading"
                >
                    Изменить пароль
                </v-btn>
            </v-form>
        </v-card>
    </v-container>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import apiClient from "../api/client";

const profile = reactive({
    email: "",
    is_active: false,
    activation_key: "",
});

const passwordForm = reactive({
    old_password: "",
    new_password: "",
    new_password_confirm: "",
});

const proxy = ref(null);
const message = ref("");
const error = ref("");
const connectionStatus = ref("");
const socketStatus = ref("disconnected");
const socket = ref(null);

const refreshLoading = ref(false);
const connectLoading = ref(false);
const passwordLoading = ref(false);

const showOldPassword = ref(false);
const showNewPassword = ref(false);
const showNewPasswordConfirm = ref(false);

const currentSocketStatus = computed(() => {
    const statuses = {
        connected: "Подключено",
        disconnected: "Отключено",
        no_free_vms: "Нет свободных прокси",
        error: "Ошибка подключения",
        waiting: "Ожидание",
    };
    return statuses[socketStatus.value] || "Ожидание";
});

const connectionStatusType = computed(() => {
    if (socketStatus.value === "connected") return "success";
    if (socketStatus.value === "no_free_vms" || socketStatus.value === "error")
        return "error";
    return "info";
});

async function loadProfile() {
    try {
        const response = await apiClient.get("/profile/");
        profile.email = response.data.email;
        profile.is_active = response.data.is_active;
        profile.activation_key = response.data.activation_key;
    } catch (err) {
        error.value = err.response?.data?.detail || "Ошибка загрузки профиля";
    }
}

function connectWebSocket() {
    socket.value = new WebSocket("ws://localhost:8000/ws/status/");

    socket.value.onmessage = (event) => {
        const data = JSON.parse(event.data);
        socketStatus.value = data.status;
        connectionStatus.value = data.message;
        if (data.proxy) proxy.value = data.proxy;
    };
}

async function refreshKey() {
    refreshLoading.value = true;
    try {
        const res = await apiClient.post("/refresh-key/");
        message.value = res.data.message;
        await loadProfile();
    } finally {
        refreshLoading.value = false;
    }
}

async function connectProxy() {
    connectLoading.value = true;

    if (!profile.activation_key) {
        error.value = "Ключ отсутствует";
        connectLoading.value = false;
        return;
    }

    try {
        const res = await apiClient.post("/activate-key/", {
            activation_key: profile.activation_key,
        });

        message.value = res.data.message;
        proxy.value = res.data.proxy;

        await loadProfile();
    } catch (err) {
        error.value = err.response?.data?.detail;
    } finally {
        connectLoading.value = false;
    }
}

async function changePassword() {
    passwordLoading.value = true;

    try {
        const res = await apiClient.post(
            "/change-password/",
            passwordForm,
        );

        message.value = res.data.message;
        Object.keys(passwordForm).forEach((k) => (passwordForm[k] = ""));
    } catch (err) {
        error.value = err.response?.data?.detail;
    } finally {
        passwordLoading.value = false;
    }
}

onMounted(() => {
    loadProfile();
    connectWebSocket();
});

onBeforeUnmount(() => {
    if (socket.value) socket.value.close();
});
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

.profile-card {
    width: 100%;
    max-width: 620px;
    padding: 28px;
    border-radius: 24px;
}

.key-text {
    word-break: break-all;
    font-family: monospace;
}

.proxy-card {
    padding: 20px;
    border-radius: 18px;
    background: #f0fdff;
    border: 1px solid #a5f3fc;
}
</style>
