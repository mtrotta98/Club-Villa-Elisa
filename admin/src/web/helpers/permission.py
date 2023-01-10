from src.web.controllers.validators import validator_permisos


def has_permission(user, permission):
    """Manda a validar al modelo si un usuario tiene los permisos necesarios para ingresar a una vista"""
    return validator_permisos.has_permission(user, permission)
