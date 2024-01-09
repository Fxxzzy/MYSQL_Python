from win10toast import ToastNotifier

def notificacion(titulo,cuerpo):
    # Crear un objeto ToastNotifier
    toast = ToastNotifier()

    # Configurar y mostrar la notificación
    toast.show_toast(titulo,
                    cuerpo,
                    duration=10)  # La duración está en segundos

    # Esperar a que se cierre la notificación
    import time
    time.sleep(12)


