from django.http import HttpRequest

class AuthRequest(HttpRequest):
    image_url = None
    user_profile = None
    role = None
    is_admin = False

    def __init__(self, *args, **kwargs):
        super(AuthRequest, self).__init__(*args, **kwargs)
        self.image_url = None
        self.user_profile = None
        self.role = None
        self.is_admin = False

    def __str__(self):
        return f'AuthRequest({self.user}, {self.user_profile}, {self.role}, {self.is_admin})'