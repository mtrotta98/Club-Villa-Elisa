import json

from flask import Blueprint, render_template, request, Response, session, abort, flash

from src.core import configuracion_sistema
from src.core import socios
from src.core import pagos
from src.web.controllers.validators.validator_configuracion import es_entero
from src.web.helpers.permission import has_permission
from src.web.exportaciones import recibo_PDF
from src.decoradores.login import login_requerido


pago_blueprint = Blueprint("pagos", __name__, url_prefix="/pagos")


def pagos_json(id):
    """Retorna el json con todos los pagos del socio logueado"""
    return json.dumps(pagos.listar_pagos_diccionario(id))


def pagos_adeudados_json(id):
    """Retorna el json con todos los pagos adeudados del socio logueado"""
    return json.dumps(pagos.listar_pagos_adeudados_diccionario(id))


def pagar_json(json, id):
    """Recibe un json que es una lista con un solo elemento que tendria datos del pago
    los datos son "month" y "amount"."""
    if not configuracion_sistema.get_configuracion_general().activar_pagos:
        return generar_respuesta("{'error':'Los pagos no estan activados'}", 400, "text")

    if not es_entero(id):
        return generar_respuesta(
            "{'error': el id enviado en el header debe ser un entero}", 400, "text"
        )
    # diccionario = json[0]
    pudo_pagar, mensaje = pagos.pagar_con_api(json, id)
    if pudo_pagar:
        return generar_respuesta(
            "{'month':'"
            + str(json["month"])
            + "', 'amount':'"
            + str(json["amount"])
            + "'}",
            201,
            "application/json",
        )
    return generar_respuesta("{'error':'" + mensaje + "'}", 400, "text")


def generar_respuesta(respuesta_json, codigo, tipo_respuesta):
    """Genera una respuesta a los pedidos a la api POST de pagos, recibe un json,
    el codigo que devuelve el servidor y el tipo de respuesta que envia"""
    return Response(respuesta_json, status=codigo, mimetype=tipo_respuesta)


@pago_blueprint.route("/socioPagos/<id>/")
@login_requerido
def pagos_socios(id):
    """Esta funcion retorna todos los pagos asociados al socio solicitado"""
    if not (has_permission(session["user"], "pago_index")):
        return abort(403)
    page = request.args.get("page", 1, type=int)
    kwargs = {
        "pagos": pagos.listar_pagos_socio(id, page),
        "id_socio": id,
    }
    return render_template("pagos/pagos_socio.html", **kwargs)


@pago_blueprint.route("/pago_de_cuota/<id>")
def pagar_cuota(id):
    """Paso de confirmacion antes de cambiar el estado de una cuota impaga a pagada"""
    if not (has_permission(session["user"], "pago_pay")):
        return abort(403)
    pago = pagos.get_cuota(id)
    if pago.estado == True:
        return pagos_socios(pago.socio.id)
    socio = socios.buscar_socio(pago.socio.id)
    if pago.total == 0:
        total = pagos.calcular_cuota(pago.id, pago.socio.id)
    else:
        total = pago.total
    kwargs = {"pago": pago, "total": total}
    return render_template("pagos/pago_de_cuota.html", **kwargs)


@pago_blueprint.route("/pago_confirmado/<id>")
def confirmar_pago(id):
    """Cambia el estado de una cuota de impaga a pagada. Persiste la fecha y monto de pago en la base de datos"""
    if not (has_permission(session["user"], "pago_pay")):
        return abort(403)
    pago = pagos.get_cuota(id)

    if pago.estado == False:
        if not pagos.pagar_cuota(id, pago.socio.id):
            flash("Error. El valor de la cuota esta fuera de rango")
            return pagos_socios(pago.socio.id)
    return pagos_socios(pago.socio.id)


@pago_blueprint.route("/descargar_pdf_recibo/<id>")
def generarRecibo(id):
    """Descarga un recibo en pdf para una cuota pagada"""
    configuracion = configuracion_sistema.get_configuracion_general()
    data_pago = {
        "encabezado": configuracion.encabezado_recibos,
        "cuota_base": configuracion.cuota_base,
        "recargo": configuracion.porcentaje_recargo,
        "pago": pagos.get_cuota(id),
    }
    if data_pago["pago"].estado == True:
        output = recibo_PDF.generar_recibo_PDF(data_pago)
        return output
    else:
        return pagos_socios(data_pago["pago"].socio.id)
