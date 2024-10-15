from enum import Enum


class TransactionType(Enum):
    PURCHASE = "purchase"
    BILL = "bill"
    TRANSFER = "transfer"
