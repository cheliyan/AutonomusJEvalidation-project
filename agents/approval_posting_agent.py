class ApprovalPostingAgent:
    """Records human decisions and simulated SAP postings; never connects to SAP."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def approve(self, transaction_id: str, actor: str = "Finance Approver") -> dict:
        return self.db_manager.record_approval(transaction_id, actor, "APPROVED")

    def reject(self, transaction_id: str, actor: str = "Finance Approver", comment: str = "") -> dict:
        return self.db_manager.record_approval(transaction_id, actor, "REJECTED", comment)

    def post(self, transaction_id: str, actor: str = "Posting Agent") -> dict:
        return self.db_manager.record_simulated_posting(transaction_id, actor)
