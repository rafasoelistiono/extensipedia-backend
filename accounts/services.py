from rest_framework_simplejwt.tokens import RefreshToken


def blacklist_refresh_token(token):
    refresh = RefreshToken(token)
    refresh.blacklist()
