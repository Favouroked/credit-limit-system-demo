from typing import List

from src.db.entities.transaction import Transaction
from src.db.ops import DBOps


class TransactionService:
    def __init__(self, db_ops: DBOps):
        self._db_ops = db_ops

    def retrieve_transaction_data(self, payload: dict) -> List[Transaction]:
        query = f"""SELECT * FROM {Transaction.get_table_name()} 
                WHERE user_id = %(user_id)s AND created_at BETWEEN %(start)s AND %(end)s"""
        result = self._db_ops.run_query(query, payload)
        return [Transaction.model_validate(r) for r in result]
