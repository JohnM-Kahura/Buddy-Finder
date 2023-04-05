import pynecone as pc
from .base_state import State, Message, Friends, User
from .helpers import navbar
import datetime


class HomeState(State):
    """The state for the home page."""

    message: str
    show_message: bool = False
    messages: list[Message] = []

    friend: str
    search: str

    def toggle_message(self):
        """Toggle the message modal."""
        self.show_message = not (self.show_message)
        return self.get_messages()

    def post_message(self):
        """Post a message."""
        if self.username == "":
            return pc.window_alert("Please log in to post a message.")
        with pc.session() as session:
            message = Message(
                username=self.username,
                message=self.message,
                time=datetime.datetime.now().strftime("%m/%d %H"),
            )
            session.add(message)
            session.commit()
        return self.toggle_message()

    def get_messages(self):
        """Get Messages from the database."""
        with pc.session() as session:
            if self.search != "":
                self.messages = (
                    session.query(Message)
                    .filter(Message.message.contains(self.search))
                    .all()[::-1]
                )
            else:
                self.messages = session.query(Message).all()[::-1]

    def set_search(self, search):
        """Set the search query."""
        self.search = search
        return self.get_messages()

    def follow_user(self, user):
        """Follow a user."""
        with pc.session() as session:
            friend = Friends(username=self.username, friend=user)
            session.add(friend)
            session.commit()

    @pc.var
    def following(self) -> list[Friends]:
        """Get a list of users the current user is following."""
        if self.logged_in:
            with pc.session() as session:
                return session.exec(
                    Friends.select.where(Friends.username == self.username)
                ).all()
        else:
            return []

    @pc.var
    def followers(self) -> list[Friends]:
        """Get a list of users following the current user."""
        if self.logged_in:
            with pc.session() as session:
                return session.exec(
                    Friends.select.where(Friends.friend == self.username)
                ).all()
        else:
            return []

    @pc.var
    def search_users(self) -> list[Friends]:
        """Get a list of users matching the search query."""
        if self.logged_in and self.friend != "":
            with pc.session() as session:
                following = session.exec(
                    Friends.select.where(Friends.username == self.username)
                ).all()
                users = session.exec(
                    User.select.where(
                        User.username == self.friend, User.username != self.username
                    )
                ).all()
                return [
                    user
                    for user in users
                    if user.username not in [friend.friend for friend in following]
                ]
        return []


def message_(State):
    """Display for an individual Message."""
    return pc.modal(
        pc.modal_overlay(
            pc.modal_content(
                pc.modal_header(
                    pc.hstack(
                        pc.icon(
                            tag="close",
                            on_click=State.toggle_message,
                            height=".8em",
                            width=".8em",
                        ),
                        pc.spacer(),
                        pc.avatar(name=State.username, size="sm"),
                        width="100%",
                    ),
                ),
                pc.modal_body(
                    pc.input(
                        on_blur=State.set_message,
                        placeholder="What's happening?",
                        width="100%",
                    ),
                ),
                pc.modal_footer(
                    pc.button(
                        "Message",
                        on_click=State.post_message,
                        bg="rgb(29 161 242)",
                        color="white",
                        border_radius="full",
                    )
                ),
            )
        ),
        is_open=State.show_message,
        border_radius="lg",
    )


def home():
    """The home page."""
    return pc.center(
        navbar(State),
        pc.hstack(
            pc.vstack(
                pc.input(
                    on_change=HomeState.set_friend,
                    placeholder="Add Friend",
                    width="100%",
                ),
                pc.foreach(
                    HomeState.search_users,
                    lambda friend: pc.vstack(
                        pc.hstack(
                            pc.avatar(name=friend.username, size="sm"),
                            pc.text(friend.username),
                            pc.spacer(),
                            pc.button(
                                pc.icon(tag="add", color="white", height="1em"),
                                on_click=lambda: HomeState.follow_user(friend.username),
                                bg="rgb(29, 161, 242)",
                            ),
                            width="100%",
                        ),
                        padding="1em",
                        width="100%",
                    ),
                ),
                pc.center(
                    pc.button(
                        "Post a message",
                        on_click=HomeState.toggle_message,
                        bg="rgb(29 161 242)",
                        color="white",
                        border_radius="full",
                        width="100%",
                    ),
                    width="100%",
                ),
                pc.divider(),
                pc.heading("Following"),
                pc.divider(),
                pc.foreach(
                    HomeState.following,
                    lambda friend: pc.vstack(
                        pc.hstack(
                            pc.avatar(name=friend.friend, size="sm"),
                            pc.text(friend.friend),
                        ),
                        padding="1em",
                    ),
                ),
                pc.heading("Buddies"),
                pc.divider(),
                pc.foreach(
                    HomeState.followers,
                    lambda friend: pc.vstack(
                        pc.hstack(
                            pc.avatar(name=friend.username, size="sm"),
                            pc.text(friend.username),
                        ),
                        padding="1em",
                    ),
                ),
                
                align_items="start",
                height="100vh",
                padding_x="1em",
                border_right="0.1em solid #F0F0F0",
                position="fixed",
                overflow_x="scroll",
            ),
            message_(HomeState),
            pc.vstack(
                pc.center(
                    pc.icon(
                        tag="chevron_up",
                        on_click=HomeState.get_messages,
                        height="2em",
                        width="2em",
                    )
                ),
                pc.input(
                    on_change=HomeState.set_search, placeholder="Search", width="100%"
                ),
                pc.foreach(
                    HomeState.messages,
                    lambda message: pc.vstack(
                        pc.hstack(
                            pc.avatar(name=message.username, size="sm"),
                            pc.text("@" + message.username),
                            pc.spacer(),
                            pc.text(message.time),
                            width="100%",
                            align_items="left",
                        ),
                        pc.divider(),
                        pc.text(message.message, width="100%"),
                        padding="1em",
                        border_color=" 1px solid #ededed",
                        border_width="1px",
                        border_radius="lg",
                        shadow="sm",
                        width="100%",
                    ),
                ),
                align_items="top",
                padding_x="5em",
                padding_left="20em",
                max_height="80%",
                width="100%",
            ),
            align_items="start",
            width="100%",
            padding_x="15%",
        ),
        padding_top="6em",
    )
