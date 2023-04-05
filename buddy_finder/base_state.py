import pynecone as pc


class User(pc.Model, table=True):
    """A table of Users."""

    username: str
    password: str


class Message(pc.Model, table=True):
    """A table of Messages."""

    username: str
    message: str
    time: str


class Friends(pc.Model, table=True):
    """A table of Friends."""

    username: str
    friend: str


class State(pc.State):
    """The base state for the app."""

    username: str
    logged_in: bool = False

    def logout(self):
        """Log out a user."""
        self.reset()
        return pc.redirect("/")
