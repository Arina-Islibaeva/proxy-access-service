import axios from "axios";

const apiClient = axios.create({
    baseURL: "http://localhost:8000/api",
    withCredentials: true,
});

// Получает значение cookie по имени
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }

    return null;
}

// Добавляем CSRF-токен в заголовки перед каждым запросом
apiClient.interceptors.request.use((config) => {
    const csrfToken = getCookie("csrftoken");

    if (csrfToken) {
        config.headers["X-CSRFToken"] = csrfToken;
    }

    return config;
});

export default apiClient;
