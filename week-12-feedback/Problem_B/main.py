import logging
from data_generator import generate_events
from processor import process_events


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

    logger = logging.getLogger("session_pipeline")

    events = generate_events()
    result = process_events(events)

    logger.info("Session processing finished")
    logger.info("completed_sessions=%s", result["completed_sessions"])
    logger.info("invalid_events=%s", result["invalid_events"])
    logger.info("total_revenue=%s", result["total_revenue"])
    logger.info("users_still_logged_in=%s", result["users_still_logged_in"])


if __name__ == "__main__":
    main()