import logging
from datetime import datetime, timedelta

from app.models.db import db
from app.models.db.starships import Starship, Manufacturer, StarshipManufacturer
from app.models.db.sync_metadata import SyncMetadata
from app.services.api_client import SWAPIClient

logger = logging.getLogger(__name__)


class SyncJob:
    @staticmethod
    def sync_starships():
        from run import application

        with application.app_context():
            current_time = datetime.utcnow()

            sync_metadata = SyncMetadata.query.filter_by(entity="starships").first()

            if not sync_metadata:
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

            try:
                SyncJob._perform_starships_sync()
            except Exception as e:
                logger.error(f"Error during synchronization: {e}")
            finally:
                sync_metadata.is_running = False
                sync_metadata.last_synced = current_time
                db.session.commit()

    @staticmethod
    def _perform_starships_sync():
        api_ids = []
        first_page_data = SWAPIClient.get_starships(page=1)
        total_pages = first_page_data["total_pages"]

        starships_summary = first_page_data.get("results", [])
        for starship_summary in starships_summary:
            api_ids.append(starship_summary["uid"])

        for page in range(2, total_pages + 1):
            data = SWAPIClient.get_starships(page=page)
            starships_summary = data.get("results", [])
            for starship_summary in starships_summary:
                api_ids.append(starship_summary["uid"])

        SyncJob._expunge_starships_not_in(api_ids)

        for uid in api_ids:
            starship_details = SWAPIClient.get_starship_by_id(uid)
            properties = starship_details["result"]["properties"]
            SyncJob._upsert_starship(uid, properties)

        logger.info("Starships synchronization completed successfully.")

    @staticmethod
    def _expunge_starships_not_in(api_ids):
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

    @staticmethod
    def _upsert_starship(sh_id: str, properties):

        from run import application
        with application.app_context():
            starship = Starship.query.filter_by(id=sh_id).first()
            if not starship:
                starship = Starship(
                    id=sh_id,
                    name=properties["name"],
                    model=properties["model"],
                    starship_class=properties["starship_class"],
                    cost_in_credits=properties.get("cost_in_credits"),
                    length=properties.get("length"),
                    crew=properties.get("crew"),
                    passengers=properties.get("passengers"),
                    max_atmosphering_speed=properties.get("max_atmosphering_speed"),
                    hyperdrive_rating=properties.get("hyperdrive_rating"),
                    MGLT=properties.get("MGLT"),
                    cargo_capacity=properties.get("cargo_capacity"),
                    consumables=properties.get("consumables"),
                    created_at=properties["created"],
                    edited_at=properties["edited"],
                    url=properties["url"],
                )
                db.session.add(starship)
            else:
                starship.id = sh_id
                starship.model = properties["model"]
                starship.starship_class = properties["starship_class"]
                starship.cost_in_credits = properties.get("cost_in_credits")
                starship.length = properties.get("length")
                starship.crew = properties.get("crew")
                starship.passengers = properties.get("passengers")
                starship.max_atmosphering_speed = properties.get("max_atmosphering_speed")
                starship.hyperdrive_rating = properties.get("hyperdrive_rating")
                starship.MGLT = properties.get("MGLT")
                starship.cargo_capacity = properties.get("cargo_capacity")
                starship.consumables = properties.get("consumables")
                starship.edited_at = properties["edited"]

            SyncJob._sync_manufacturers(starship, properties["manufacturer"])

    @staticmethod
    def _sync_manufacturers(starship, manufacturer_data):
        from run import application
        with application.app_context():
            manufacturers = manufacturer_data.split(", ")
            for manufacturer_name in manufacturers:
                manufacturer = Manufacturer.query.filter_by(name=manufacturer_name).first()
                if not manufacturer:
                    manufacturer = Manufacturer(name=manufacturer_name)
                    db.session.add(manufacturer)

                if not StarshipManufacturer.query.filter_by(
                        starship_id=starship.id, manufacturer_id=manufacturer.id
                ).first():
                    relation = StarshipManufacturer(starship_id=starship.id, manufacturer_id=manufacturer.id)
                    db.session.add(relation)
