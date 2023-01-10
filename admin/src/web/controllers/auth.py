from flask import Blueprint, render_template, request, flash, url_for, session, redirect

from src.core import usuarios
from src.web.controllers.validators import validator_usuario


auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@auth_blueprint.get("/")
def login():
    """Esta funcion retorna el template para logearse"""
    return render_template("auth/login.html")


@auth_blueprint.post("/authenticate")
def authenticate():
    """Esta funcion realiza la autenticacion de un usuario"""
    params = request.form
    validacion, mensaje = validator_usuario.validar_inputs(
        params["email"], params["password"], {"ROL_ADMINISTRADOR": "ignorar"}
    )
    if not validacion:
        flash(mensaje, "error")
        return redirect(url_for("auth.login"))
    user = usuarios.find_user_by_mail_and_pass(params["email"], params["password"])
    if user is None:
        flash("Credenciales invalidas", "error")
        return redirect(url_for("auth.login"))
    elif user.activo == False:
        flash("Usted no tiene permitido acceder al sistema", "error")
        return redirect(url_for("auth.login"))
    session["user"] = user.email
    session["nombre"] = user.nombre
    session["apellido"] = user.apellido
    flash("Sesión iniciada correctamente")
    return redirect(url_for("home"))


@auth_blueprint.get("/logout")
def logout():
    """Esta funcion realiza el logout de un usuario"""
    session.pop("user", None)
    flash("Sesión cerrada correctamente")
    return redirect(url_for("auth.login"))
