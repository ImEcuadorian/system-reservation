import datetime
import Pyro4
from room import Room

rooms = [
    Room("Room A"),
    Room("Room B"),
    Room("Room C"),
]

reservations = []

@Pyro4.expose
class RoomManager:

    def list_rooms(self):
        return [room.name for room in rooms]

    def check_availability(self, room, date, start_time, end_time):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.datetime.strptime(end_time, "%H:%M").time()
        for r in reservations:
            if r['room'] == room and r['date'] == date:
                if not (end_time <= r['start_time'] or start_time >= r['end_time']):
                    return False
        return True

    def reserve_room(self, username, room, date, start_time, end_time):
        auth = Pyro4.Proxy("PYRONAME:auth_server")
        if not auth.is_logged_in(username):
            return "User not logged in"

        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start = datetime.datetime.strptime(start_time, "%H:%M").time()
        end = datetime.datetime.strptime(end_time, "%H:%M").time()

        now = datetime.datetime.now()
        initial = datetime.datetime.combine(date, start)
        end = datetime.datetime.combine(date, end)
        duration = (end - initial).total_seconds() / 60

        if initial < now:
            return "You can't reserve a room in the past"
        if duration < 30 or duration > 240:
            return "The duration must be between 30 and 4 hours"

        user_reservations = [r for r in reservations if r['username'] == username and r['date'] == date]
        if len(user_reservations) >= 2:
            return "You can't reserve more than 2 rooms at the same time"

        if not self.check_availability(room, date, start_time, end_time):
            return "Room not available"

        reservations.append({
            'username': username,
            'room': room,
            'date': date,
            'start_time': start,
            'end_time': end
        })
        return "Room reserved successfully"

    def cancel_reservation(self, username, room, date, start_time, end_time):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start = datetime.datetime.strptime(start_time, "%H:%M").time()
        end = datetime.datetime.strptime(end_time, "%H:%M").time()
        for r in reservations:
            if (r['username'] == username and r['room'] == room and r['date'] == date and
                r['start_time'] == start and r['end_time'] == end):
                reservations.remove(r)
                return "Reservation cancelled successfully"
        return "Reservation not found"

    def get_user_reservations(self, username):
        now = datetime.datetime.now()
        return [
            {
                'room': r['room'],
                'date': r['date'].strftime("%Y-%m-%d"),
                'start_time': r['start_time'].strftime("%H:%M"),
                'end_time': r['end_time'].strftime("%H:%M")
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