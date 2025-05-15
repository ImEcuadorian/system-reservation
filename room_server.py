import datetime
import Pyro4
from room import Room

rooms = [
    Room("Sala A"),
    Room("Sala B"),
    Room("Sala C"),
]

reservations = []

@Pyro4.expose
class RoomManager:

    def list_rooms(self):
        return [room.name for room in rooms]

    def check_availability(self, room, date:str, start_time, end_time):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.datetime.strptime(end_time, "%H:%M").time()
        for r in reservations:
            if r['room'] == room and r['date'] == date:
                if not (end_time <= r['start_time'] or start_time >= r['end_time']):
                    return False
        return True

    def reserve_room(self, username, room, d:str, start_time, end_time):
        auth = Pyro4.Proxy("PYRONAME:auth_server")
        if not auth.is_logged_in(username):
            return "Usuario no autenticado"

        fecha = datetime.datetime.strptime(d, "%Y-%m-%d").date()
        start = datetime.datetime.strptime(start_time, "%H:%M").time()
        end_obj = datetime.datetime.strptime(end_time, "%H:%M").time()

        now = datetime.datetime.now()
        reserva_inicio = datetime.datetime.combine(fecha, start)
        reserva_fin = datetime.datetime.combine(fecha, end_obj)
        duracion = (reserva_fin - reserva_inicio).total_seconds() / 60

        if reserva_inicio < now:
            return "No se puede reservar en el pasado"
        if duracion < 30 or duracion > 240:
            return "La reserva debe ser entre 30 minutos y 4 horas"

        reservas_usuario = [r for r in reservations if r['username'] == username and r['date'] == d]
        if len(reservas_usuario) >= 2:
            return "No puede reservar más de 2 veces el mismo día"

        reservations.append({
            'username': username,
            'room': room,
            'date': fecha,
            'start_time': start,
            'end_time': end_obj
        })
        return "Reserva realizada con éxito"

    def cancel_reservation(self, username, room, date, start_time, end_time):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start = datetime.datetime.strptime(start_time, "%H:%M").time()
        end = datetime.datetime.strptime(end_time, "%H:%M").time()
        for r in reservations:
            if (r['username'] == username and r['room'] == room and r['date'] == date and
                r['start_time'] == start and r['end_time'] == end):
                reservations.remove(r)
                return "Reserva cancelada"
        return "No se encontró la reserva o no tiene permisos para cancelarla"

    def get_user_reservations(self, username):
        now = datetime.datetime.now()
        return [
            {
                'room': r['room'],
                'date': r['date'],
                'start_time': r['start_time'],
                'end_time': r['end_time']
            }
            for r in reservations
            if r['username'] == username and
               datetime.datetime.combine(r['date'], r['end_time']) > now
        ]

def main():
    daemon = Pyro4.Daemon()
    uri = daemon.register(RoomManager)
    print("Room Manager Server URI", uri)
    Pyro4.locateNS().register("room_server", uri)
    daemon.requestLoop()

if __name__ == "__main__":
    main()