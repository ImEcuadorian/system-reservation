import Pyro4

users = [
    {"username": "user1", "password": "pass1"},
    {"username": "user2", "password": "pass2"},
]

user_connections = {}


@Pyro4.expose
class AuthServer:

    def login(self, username, password):
        for user in users:
            if user["username"] == username and user["password"] == password:
                return "Login successful"
        return "Invalid credentials"

    def connected_users(self, username):
        if self.is_logged_in(username):
            return "User is logged in"
        else:
            user_connections[username] = True
            print(user_connections)
            return "User added to connected users"

    def is_logged_in(self, username):
        if username in user_connections:
            return True
        return None

def main():
    daemon = Pyro4.Daemon()
    uri = daemon.register(AuthServer)
    print("Auth Server URI", uri)
    Pyro4.locateNS().register("auth_server", uri)
    daemon.requestLoop()

if __name__ == "__main__":
    main()