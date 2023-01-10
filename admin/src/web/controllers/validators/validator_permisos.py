from src.core import usuarios, permisos


def has_permission(user, permission):
    """Este metodo valida si el usuario posee o no el permiso enviado por parametro"""
    usuario = usuarios.buscar_usuario_email(user)
    roles = usuario.roles
    permiso = permisos.buscar_permiso(permission)
    for rol in roles:
        if (permiso in rol.permisos):
            return True
    return False