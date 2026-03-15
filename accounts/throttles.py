from rest_framework.throttling import AnonRateThrottle


class AdminLoginBurstThrottle(AnonRateThrottle):
    scope = "admin_login_burst"


class AdminLoginSustainedThrottle(AnonRateThrottle):
    scope = "admin_login_sustained"
