class HumanApprovalManager:
    """
    Stores approval status for requests.

    For now, approval is stored in memory.

    Later this can be replaced by
    Redis / Database / Flask Session.
    """

    WAITING = "WAITING_FOR_CONFIRMATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

    def __init__(self):
        self.requests = {}

    def start(self, request_id, message):
        self.requests[request_id] = {
            "status": self.WAITING,
            "message": message
        }

    def approve(self, request_id):
        if request_id in self.requests:
            self.requests[request_id]["status"] = self.APPROVED

    def reject(self, request_id):
        if request_id in self.requests:
            self.requests[request_id]["status"] = self.REJECTED

    def get_status(self, request_id):
        request = self.requests.get(request_id)
        if request:
            return request["status"]
        return None

    def get_message(self, request_id):
        request = self.requests.get(request_id)
        if request:
            return request["message"]
        return None

    def remove(self, request_id):
        self.requests.pop(request_id, None)