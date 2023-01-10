import json

from flask import Blueprint, render_template, request, flash, redirect, session, abort

from src.core import usuarios
from src.web.helpers.permission import has_permission
from src.web.controllers.validators import validator_usuario
from src.decoradores.login import login_requerido


usuario_blueprint = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuario_blueprint.route("/")
@login_requerido
def usuario_index():
    """Esta funcion llama al modulo correspondiente para obtener todos los usuarios paginados."""
    if not (has_permission(session["user"], "usuario_index")):
        return abort(403)
    page = request.args.get("page", 1, type=int)
    email = (
        request.args.get("busqueda", type=str)
        if request.args.get("busqueda", type=str) != ""
        else None
    )
    tipo = (
        request.args.get("tipo", type=str)
        if request.args.get("tipo", type=str) != ""
        else None
    )
    kwargs = {
        "usuarios": usuarios.listar_usuarios(page, email, tipo),
        "email": email,
        "tipo": tipo,
        "usuario": usuarios.buscar_usuario_email(session["user"]),
    }
    return render_template("usuarios/index.html", **kwargs)


@usuario_blueprint.route("/alta-usuario")
@login_requerido
def form_usuario():
    """Esta funcion devuelve el template con un formulario para dar de alta un usuario"""
    if not (has_permission(session["user"], "usuario_new")):
        return abort(403)
    kwargs = {"usuario": usuarios.buscar_usuario_email(session["user"])
    }
    return render_template("usuarios/alta_usuarios.html", **kwargs)


@usuario_blueprint.route("/<id>")
@login_requerido
def usuario_profile(id):
    """Esta funcion llama al modulo correspondiente para obtener a un usuario por su id."""
    kwargs = {
        "usuario": usuarios.buscar_usuario(id),
        "rol": usuarios.verificar_rol_usuario(id),
    }
    return render_template("usuarios/perfil_usuario.html", **kwargs)


@usuario_blueprint.route("/alta", methods=["POST"])
@login_requerido
def usuario_add():
    """Esta funcion llama al metodo correspondiente para dar de alta un usuario.
    Si recibe un 1 es porque ese dni ya esta cargado, si devuelve un 2 es porque ese mail ya esta cargado."""
    data_usuario = {
        "nombre": request.form.get("nombre").capitalize(),
        "apellido": request.form.get("apellido").capitalize(),
        "email": request.form.get("email"),
        "activo": True,
        "username": request.form.get("username"),
        "password": request.form.get("password"),
    }
    data_rol_usuario = {
        "ROL_ADMINISTRADOR": request.form.get("rol_administrador"),
        "ROL_OPERADOR": request.form.get("rol_operador"),
    }
    validacion_inputs, mensaje = validator_usuario.validar_inputs(
        data_usuario["email"], data_usuario["password"], data_rol_usuario
    )
    if validacion_inputs == False:
        flash(mensaje)
        return redirect("/usuarios/alta-usuario")
    validacion, mensaje = usuarios.validar_datos_existentes(
        data_usuario["email"], data_usuario["username"], "alta"
    )
    if validacion == False:
        flash(mensaje)
        return redirect("/usuarios/alta-usuario")
    else:
        usuario = usuarios.agregar_usuario(data_usuario)
        usuarios.agregar_roles(usuario, data_rol_usuario)
    return redirect("/usuarios")


@usuario_blueprint.route("/modificacion", methods=["POST"])
@login_requerido
def usuario_update():
    """Esta funcion llama al metodo correspondiente para modificar los datos de un usuario."""
    if not (has_permission(session["user"], "usuario_update")):
        return abort(403)
    if usuarios.verificar_rol_usuario(request.form.get("id")):
        estado = True
    else:
        estado = usuarios.validar_estado(request.form.get("activo"))
    data_usuario = {
        "id": request.form.get("id"),
        "nombre": request.form.get("nombre").capitalize(),
        "apellido": request.form.get("apellido").capitalize(),
        "email": request.form.get("email"),
        "activo": estado,
        "username": request.form.get("username"),
    }
    validacion, mensaje = usuarios.validar_datos_existentes(
        data_usuario["email"],
        data_usuario["username"],
        "modificacion",
        data_usuario["id"],
    )
    if validacion == False:
        flash(mensaje)
        return redirect("/usuarios/" + data_usuario["id"])
    else:
        usuarios.modificar_usuario(data_usuario)
    return redirect("/usuarios")


@usuario_blueprint.route("/eliminar/<id>", methods=["POST", "GET"])
@login_requerido
def usuario_delete(id):
    """Esta funcion llama al metodo correspondiente para eliminar un usuario."""
    if not (has_permission(session["user"], "usuario_destroy")):
        return abort(403)
    usuarios.eliminar_usuario(id)
    return redirect("/usuarios")

