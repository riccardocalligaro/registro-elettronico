class AuthenticationFailedError(Exception):
    """
    Authentication failed error: bad username or password
    """

    def __init__(self):
        self.message = "Bad username or password"


class NotLoggedInError(Exception):
    """
    Not logged in error: you must logged in to use this method
    """

    def __init__(self):
        self.message = "You must logged in to use this method."
