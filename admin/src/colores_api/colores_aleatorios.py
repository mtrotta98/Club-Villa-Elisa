import random

def generar_color():
    color = "#"
    hexadecimal = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
    for i in range(6):
        color += random.choice(hexadecimal)
    return color