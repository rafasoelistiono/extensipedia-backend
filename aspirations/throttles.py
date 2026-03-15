from rest_framework.throttling import AnonRateThrottle


class PublicAspirationSubmitBurstThrottle(AnonRateThrottle):
    scope = "aspiration_submit_burst"


class PublicAspirationSubmitSustainedThrottle(AnonRateThrottle):
    scope = "aspiration_submit_sustained"


class PublicAspirationInteractionBurstThrottle(AnonRateThrottle):
    scope = "aspiration_interaction_burst"


class PublicAspirationInteractionSustainedThrottle(AnonRateThrottle):
    scope = "aspiration_interaction_sustained"


class PublicTicketTrackingThrottle(AnonRateThrottle):
    scope = "ticket_tracking"
