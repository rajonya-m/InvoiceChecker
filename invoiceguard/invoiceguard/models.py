"""The Invoice class (CONCEPT: classes, objects, __init__, methods)."""


class Invoice:
    def __init__(self, invoice_no, vendor_name, gstin, invoice_date, amount,
                 email, description="", state="", flags=None,
                 risk_score=0, risk_level="Low"):
        self.invoice_no = invoice_no
        self.vendor_name = vendor_name
        self.gstin = gstin
        self.invoice_date = invoice_date      # a datetime.date object
        self.amount = amount                  # a float
        self.email = email
        self.description = description
        self.state = state
        self.flags = flags if flags is not None else []   # list of codes
        self.risk_score = risk_score
        self.risk_level = risk_level

    def to_dict(self):
        """Turn the object into a plain dictionary (good for JSON / API)."""
        return {
            "invoice_no": self.invoice_no,
            "vendor_name": self.vendor_name,
            "gstin": self.gstin,
            "state": self.state,
            "invoice_date": self.invoice_date.isoformat(),
            "amount": self.amount,
            "email": self.email,
            "description": self.description,
            "flags": self.flags,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
        }

    def __repr__(self):
        return f"Invoice({self.invoice_no}, {self.vendor_name}, {self.amount})"
