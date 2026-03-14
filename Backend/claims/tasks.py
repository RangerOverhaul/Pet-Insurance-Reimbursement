"""
Simulated async background task.
In production this would be a Celery task decorated with @shared_task.
Here we use Python threading to simulate async processing without requiring
a message broker.
"""
import threading
import time
import logging

logger = logging.getLogger(__name__)


def _process_claim(claim_id: int):
    """Runs in a background thread to simulate invoice extraction + validation."""
    import django
    from django.db import connection

    # Simulate async delay (invoice extraction)
    time.sleep(2)

    # Import inside thread to avoid app-loading issues
    from claims.models import Claim

    try:
        claim = Claim.objects.select_related("pet").get(id=claim_id)

        # Simulate: extract invoice data & validate coverage period
        pet = claim.pet
        date_covered = pet.is_date_covered(claim.date_of_event)
        invoice_date_covered = pet.is_date_covered(claim.invoice_date)

        if date_covered and invoice_date_covered:
            claim.status = Claim.Status.IN_REVIEW
            claim.review_notes = "Automated validation passed. Awaiting support review."
        else:
            claim.status = Claim.Status.REJECTED
            claim.review_notes = (
                "Automated validation failed: event date or invoice date "
                "is outside the active coverage period."
            )

        claim.save(update_fields=["status", "review_notes", "updated_at"])
        logger.info(f"Claim #{claim_id} processed → {claim.status}")

    except Claim.DoesNotExist:
        logger.error(f"Claim #{claim_id} not found during background processing.")
    finally:
        connection.close()


def process_claim_async(claim_id: int):
    """Kicks off background processing in a daemon thread."""
    thread = threading.Thread(target=_process_claim, args=(claim_id,), daemon=True)
    thread.start()
    logger.info(f"Background processing started for Claim #{claim_id}")