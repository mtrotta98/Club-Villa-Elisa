<template>
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        No se subió el comprobante o su formato es incorrecto.
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"
            v-on:click="swapEsconder"></button>
    </div>
    <h1 style="text-align:center">
        <strong>Pagar</strong>
    </h1>
    <div style="text-align:center;">
        <h2>Subir comprobante (debe ser .jpg / .png / .pdf)</h2>
        <input type="file" @change="seSubeArchivo">
        <button type="button" v-on:click="pagar()" class="btn btn-primary">Pagar</button>
    </div>
</template>
<script>
import { apiService } from "@/api";
export default {
    data() {
        return {
            cuota: null,
            comprobante: null,
            extension: "",
            error: false
        };
    },
    methods: {
        swapEsconder() {
            this.error = false;
        },
        seSubeArchivo(event) {
            this.comprobante = event.target.files[0];
            this.extension = this.comprobante.name.split(".")[1]
        },
        esArchivoValido() {
            if (this.comprobante == null) {
                return false;
            }
            return this.extension == "pdf" || this.extension == "png" || this.extension == "jpg"
        },
        pagar() {
            if (!this.esArchivoValido()) {
                this.error = true;
                return
            }
            const json = JSON.stringify({ month: this.$route.query.month, amount: this.$route.query.amount })
            const options = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            apiService
                .post("/api/me/payments", json, options)
                .then(() => {
                    this.$router.push("/pagos");
                })
                .catch((e) => {
                    console.log(e);
                });
        }
    }
}
</script>
