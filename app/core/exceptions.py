

class TicketFlowError(Exception):

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

class EventNotFoundError(TicketFlowError):
    def __init__(self, event_id: str) -> None:
        message = f"Event with id {event_id} not found"
        super().__init__(message)


class EventConflictError(TicketFlowError):
    pass

class TicketTierNotFoundError(TicketFlowError):
    def __init__(self, tier_id: str) -> None:
        super().__init__(f"Ticket tier with id {tier_id} not found")