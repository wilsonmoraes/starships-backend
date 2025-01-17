import logging
from datetime import datetime, timedelta

from app.models.db import db
from app.models.db.starships import Starship, Manufacturer, starship_manufacturer
from app.models.db.sync_metadata import SyncMetadata
from app.services.api_client import SWAPIClient

logger = logging.getLogger(__name__)


def parse_numeric_value(value, data_type=float):
    if not value or value.lower() == 'unknown':
        return None
    if not value:
        return None
    try:
        return data_type(value.replace(",", ""))
    except ValueError:
        logger.debug(f"Could not parse value '{value}' to {data_type}. Returning None.")
        return None


class SyncJob:
    @staticmethod
    def sync_starships():
        from run import application

        logger.info("Starting starships synchronization process...")
        with application.app_context():
            current_time = datetime.utcnow()

            sync_metadata = SyncMetadata.query.filter_by(entity="starships").first()

            if not sync_metadata:
                logger.info("Creating initial SyncMetadata entry for starships.")
                sync_metadata = SyncMetadata(entity="starships", last_synced=None, is_running=False)
                db.session.add(sync_metadata)
                db.session.commit()

            if sync_metadata.is_running:
                if sync_metadata.last_synced and sync_metadata.last_synced < current_time - timedelta(hours=5):
                    logger.warning("Synchronization stuck for over 5 hours. Restarting...")
                else:
                    logger.info("Another synchronization is already in progress. Aborting...")
                    return

            sync_metadata.is_running = True
            db.session.commit()
            logger.info("Marked synchronization as in progress.")

            try:
                SyncJob._perform_starships_sync()
            except Exception as e:
                logger.error(f"Error during synchronization: {e}")
            finally:
                sync_metadata.is_running = False
                sync_metadata.last_synced = current_time
                db.session.commit()
                logger.info("Synchronization process completed.")

    @staticmethod
    def _perform_starships_sync():
        api_ids = []
        first_page_data = SWAPIClient.get_starships(page=1)
        total_pages = first_page_data["total_pages"]

        starships_summary = first_page_data.get("results", [])
        for starship_summary in starships_summary:
            api_ids.append(starship_summary["uid"])
        logger.debug(f"Fetched data for page 1 with {len(starships_summary)} starships.")

        for page in range(2, total_pages + 1):
            logger.debug(f"Fetching data for page {page}...")
            data = SWAPIClient.get_starships(page=page)
            starships_summary = data.get("results", [])
            for starship_summary in starships_summary:
                api_ids.append(starship_summary["uid"])

        logger.info(f"Fetched data for all {total_pages} pages. Total starships: {len(api_ids)}")

        SyncJob._expunge_starships_not_in(api_ids)

        for uid in api_ids:
            starship_details = SWAPIClient.get_starship_by_id(uid)
            properties = starship_details["result"]["properties"]
            SyncJob._upsert_starship(uid, properties)

        logger.info("Starships synchronization completed successfully.")

    @staticmethod
    def _expunge_starships_not_in(api_ids):
        logger.info("Expunging starships not present in the API...")

        from run import application
        with application.app_context():
            batch_size = 900
            db_ids = Starship.query.with_entities(Starship.id).all()
            db_ids = [str(record.id) for record in db_ids]

            ids_to_keep = set(api_ids)
            ids_to_delete = [curr_id for curr_id in db_ids if curr_id not in ids_to_keep]

            for i in range(0, len(ids_to_delete), batch_size):
                batch = ids_to_delete[i:i + batch_size]
                Starship.query.filter(Starship.id.in_(batch)).delete(synchronize_session=False)

            db.session.commit()
        logger.info("Expunge operation completed.")

    @staticmethod
    def _upsert_starship(sh_id: str, properties):
        logger.debug(f"Upserting starship with ID {sh_id}.")

        from run import application
        with application.app_context():
            logger.info(f"Updating existing starship with ID {sh_id}.")

            starship = Starship.query.filter_by(id=sh_id).first()
            if not starship:
                starship = Starship(
                    id=sh_id,
                    name=properties["name"],
                    model=properties["model"],
                    starship_class=properties["starship_class"],
                    cost_in_credits=parse_numeric_value(properties.get("cost_in_credits"), float),
                    length=parse_numeric_value(properties.get("length"), float),
                    crew=parse_numeric_value(properties.get("crew"), int),
                    passengers=parse_numeric_value(properties.get("passengers"), int),
                    max_atmosphering_speed=properties.get("max_atmosphering_speed"),
                    hyperdrive_rating=properties.get("hyperdrive_rating"),
                    MGLT=properties.get("MGLT"),
                    cargo_capacity=properties.get("cargo_capacity"),
                    consumables=properties.get("consumables"),
                    created_at=datetime.fromisoformat(properties["created"].replace("Z", "+00:00")),
                    edited_at=datetime.fromisoformat(properties["edited"].replace("Z", "+00:00")),
                    url=properties["url"],
                )
                db.session.add(starship)
            else:
                starship.id = sh_id
                starship.model = properties["model"]
                starship.starship_class = properties["starship_class"]
                starship.cost_in_credits = parse_numeric_value(properties.get("cost_in_credits"), float)
                starship.length = parse_numeric_value(properties.get("length"), float)
                starship.crew = parse_numeric_value(properties.get("crew"), int)
                starship.passengers = parse_numeric_value(properties.get("passengers"), int)
                starship.max_atmosphering_speed = properties.get("max_atmosphering_speed")
                starship.hyperdrive_rating = properties.get("hyperdrive_rating")
                starship.MGLT = properties.get("MGLT")
                starship.cargo_capacity = properties.get("cargo_capacity")
                starship.consumables = properties.get("consumables")
                starship.edited_at = datetime.fromisoformat(properties["edited"].replace("Z", "+00:00"))
            db.session.commit()

            SyncJob._sync_manufacturers(starship, properties["manufacturer"])

    @staticmethod
    def _sync_manufacturers(starship, manufacturer_data):
        logger.debug(f"Syncing manufacturers for starship ID {starship.id}.")

        from run import application
        with application.app_context():
            manufacturers = manufacturer_data.split(", ")
            for manufacturer_name in manufacturers:
                manufacturer = Manufacturer.query.filter_by(name=manufacturer_name).first()
                if not manufacturer:
                    logger.info(f"Creating new manufacturer: {manufacturer_name}.")
                    manufacturer = Manufacturer(name=manufacturer_name)
                    db.session.add(manufacturer)
                    db.session.commit()

                relation_exists = db.session.query(
                    db.exists().where(
                        starship_manufacturer.c.starship_id == starship.id,
                        starship_manufacturer.c.manufacturer_id == manufacturer.id
                    )
                ).scalar()

                if not relation_exists:
                    logger.info(f"Adding relation between starship {starship.id} and manufacturer {manufacturer.id}.")
                    stmt = starship_manufacturer.insert().values(
                        starship_id=starship.id,
                        manufacturer_id=manufacturer.id
                    )
                    db.session.execute(stmt)
                    db.session.commit()
