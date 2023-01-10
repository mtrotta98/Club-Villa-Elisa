from flask import Blueprint, make_response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from flask_jwt_extended import create_access_token, set_access_cookies

from src.core.socios import find_socio_by_email_and_pass
from src.web.controllers import disciplinas
from src.web.controllers import socios
from src.web.controllers import configuracion_sistema
from src.web.controllers import pagos
from src.web.controllers.socios import json_informacion_socio
from src.web.controllers.validators import validator_usuario

api_blueprint = Blueprint("api", __name__, url_prefix="/api")


@api_blueprint.get("/club/disciplinas")
def obtener_disciplinas():
    """Retorna un json con todas las disciplinas que se practican en el club"""
    respuesta = make_response(disciplinas.disciplina_json(), 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.get("/club/socios-años")
def socios_por_año():
    """Retorna un json con la cantidad de socios por año"""
    respuesta = make_response(socios.socios_por_año(), 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.get("/club/socios-genero")
def socios_genero():
    """Retorna un json con la cantidad de socios por genero"""
    respuesta = make_response(socios.socios_genero(), 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.get("/club/socios-disciplinas")
def obtener_socios_disciplinas():
    """Retorna un json con los socios por disciplinas"""
    respuesta = make_response(disciplinas.disciplinas_socios(), 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.get("/club/info")
def obtener_info_club():
    """Retorna el json con la información de contacto del club"""
    respuesta = make_response(configuracion_sistema.info_contacto_json(), 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.get("/me/disciplinas")
@jwt_required()
def obtener_disciplinas_socio():
    """Retorna el json con todas las disciplinas que realiza
    el socio que está logueado actualmente en la app pública (JWT)"""
    respuesta = make_response(socios.disciplinas_socio(get_jwt_identity()), 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.get("/me/license")
@jwt_required()
def obtener_info_y_estado_socio():
    """Retorna el json con el estado de credencial y los datos
    del socio que está logueado actualmente en la app pública (JWT)"""
    respuesta = make_response(socios.json_estado_socio(get_jwt_identity()), 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.get("/me/profile")
@jwt_required()
def obtener_info_socio():
    """Retorna el json con todos los datos
    del socio que está logueado actualmente en la app pública (JWT)"""
    pass


@api_blueprint.get("/me/payments")
@jwt_required()
def obtener_pagos_socio():
    """Retorna la lista de pagos registrados
    del socio que está logueado actualmente en la app pública (JWT)"""
    respuesta = make_response(pagos.pagos_json(get_jwt_identity()), 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.get("/me/pending_payments")
@jwt_required()
def obtener_pagos_adeudados_socio():
    """Retorna la lista de pagos adeudados
    del socio que está logueado actualmente en la app pública (JWT)"""
    respuesta = make_response(pagos.pagos_adeudados_json(get_jwt_identity()), 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.post("/me/payments")
@jwt_required()
def registrar_pago_socio():
    """Registra un nuevo pago para
    el socio que está logueado actualmente en la app pública (JWT)"""
    pagos_json = pagos.pagar_json(request.get_json(), get_jwt_identity())
    respuesta = make_response(pagos_json, 200)
    respuesta.headers["Content-Type"] = "application/json"
    return respuesta


@api_blueprint.post("/auth")
def auth():
    """Esta funcion recibe la peticion de la api de login, en caso de estar todo correcto loguea al usuario y devuelve el token
    jwt"""
    if not (request.data):
        return jsonify(message="No se envió un json."), 400
    json = request.get_json()
    if not (("email") in json.keys() and ("password") in json.keys()):
        return jsonify(message="No se envió el email o la password."), 400
    validacion, mensaje = validator_usuario.validar_inputs_publico(
        json["email"], json["password"]
    )
    if not validacion:
        return jsonify(message=mensaje), 400
    socio = find_socio_by_email_and_pass(json["email"], json["password"])
    if socio is None:
        return jsonify(message="Credenciales Invalidas"), 400
    access_token = create_access_token(identity=socio.id)
    response = jsonify(access_token)
    set_access_cookies(response, access_token)
    return response, 201


@api_blueprint.get("/logout_publico")
@jwt_required()
def logout_publico():
    """Esta funcion desloguea a un socio de la app publica"""
    response = jsonify()
    unset_jwt_cookies(response)
    return response, 200


@api_blueprint.get("/socio_jwt")
@jwt_required()
def socio_jwt():
    """Esta funcion se ejecuta a la vez que el auth de la app publica, devuelve la informacion del socio en caso
    que el logueo sea exitoso"""
    socio_actual = get_jwt_identity()
    response = make_response(json_informacion_socio(socio_actual))
    return response, 200
