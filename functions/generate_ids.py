import uuid

def generate_transaction_and_reference_ids():
    transaction_id = str(uuid.uuid4())  # Generates a unique transaction ID
    reference_id = str(uuid.uuid4())  # Generates a unique reference ID
    return transaction_id, reference_id
