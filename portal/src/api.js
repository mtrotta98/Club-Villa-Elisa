import axios from "axios";

const apiService = axios.create({
  // http://localhost:5000   -> baseURL para correr localmente
  // https://admin-grupo23.proyecto2022.linti.unlp.edu.ar    -> baseURL para correr en produccion
  baseURL: "http://localhost:5000",
  withCredentials: true,
  xsrfCookieName: "csrf_access_token",
});

export { apiService };
