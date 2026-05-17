from rest_framework.throttling import AnonRateThrottle


class PublicActivityEventThrottle(AnonRateThrottle):
    scope = "activity_event"
