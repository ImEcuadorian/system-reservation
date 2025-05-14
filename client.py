import Pyro4


def main():
    auth = Pyro4.Proxy("PYRONAME:auth_server")
    room = Pyro4.Proxy("PYRONAME:room_server")
    print("Welcome to the Room Booking System")

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    login_response = auth.login(username, password)
    if login_response == "Login successful":
        auth.connected_users(username)
        while True:

            print(f"Welcome, {username}!")
            print("1. View available rooms")
            print("2. Check room availability")
            print("3. Book a room")
            print("4. Cancel booking")
            print("5. View my bookings")
            print("6. Logout")

            choice = input("Enter your choice: ")

            if choice == "1":
                rooms = room.list_rooms()
                print("Available rooms:", rooms)

            elif choice == "2":
                room_name = input("Enter room name: ")
                date = input("Enter date (YYYY-MM-DD): ")
                start_time = input("Enter start time (HH:MM): ")
                end_time = input("Enter end time (HH:MM): ")

                availability = room.check_availability(room_name, date, start_time, end_time)
                if availability:
                    print(f"Room {room_name} is available from {start_time} to {end_time} on {date}")
                else:
                    print(f"Room {room_name} is not available from {start_time} to {end_time} on {date}")

            elif choice == "3":
                room_name = input("Enter room name: ")
                date = input("Enter date (YYYY-MM-DD): ")
                start_time = input("Enter start time (HH:MM): ")
                end_time = input("Enter end time (HH:MM): ")

                booking_response = room.reserve_room(username,room_name, date, start_time, end_time)
                print(booking_response)

            elif choice == "4":
                room_name = input("Enter room name: ")
                date = input("Enter date (YYYY-MM-DD): ")
                start_time = input("Enter start time (HH:MM): ")
                end_time = input("Enter end time (HH:MM): ")

                cancel_response = room.cancel_reservation(username, room_name, date, start_time, end_time)
                print(cancel_response)

            elif choice == "5":
                bookings = room.get_user_reservations(username)
                if bookings:
                    print("Your bookings:", bookings)
                else:
                    print("No bookings found.")

            elif choice == "6":
                break

            else:
                print("Invalid choice. Please try again.")
    else:
        print("Invalid credentials. Please try again.")


if __name__ == "__main__":
    main()
