from datetime import datetime

from app import db
from app.models.db.starships import Starship, Manufacturer, StarshipManufacturer
from app.models.db.sync_metadata import SyncMetadata
from app.services.api_client import SWAPIClient


class SyncJob:
    @staticmethod
    def sync_starships():
        """
        Sincroniza as informações de starships com base na API SWAPI.
        Faz insert ou update apenas se o campo 'edited' for maior que 'last_synced'.
        """
        # Obter a última sincronização
        sync_metadata = SyncMetadata.query.filter_by(entity="starships").first()
        last_synced = sync_metadata.last_synced if sync_metadata else datetime.min

        # Inicializar paginação
        page = 1
        while True:
            data = SWAPIClient.get_starships(page=page)
            starships = data.get("results", [])
            if not starships:
                break  # Fim da paginação

            for starship_data in starships:
                properties = starship_data["properties"]

                # Verificar se o registro foi editado após o último sync
                edited_date = datetime.fromisoformat(properties["edited"].replace("Z", "+00:00"))
                if edited_date > last_synced:
                    SyncJob._upsert_starship(properties)

            page += 1

        # Atualizar a tabela de controle de sincronização
        if not sync_metadata:
            sync_metadata = SyncMetadata(entity="starships", last_synced=datetime.utcnow())
            db.session.add(sync_metadata)
        else:
            sync_metadata.last_synced = datetime.utcnow()

        db.session.commit()

    @staticmethod
    def _upsert_starship(properties):
        """
        Faz o insert ou update de uma starship no banco.
        """
        # Verificar se a starship já existe no banco
        starship = Starship.query.filter_by(name=properties["name"]).first()
        if not starship:
            starship = Starship(
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
            # Atualizar os campos da starship existente
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

        # Sincronizar fabricantes
        SyncJob._sync_manufacturers(starship, properties["manufacturer"])

    @staticmethod
    def _sync_manufacturers(starship, manufacturer_data):
        """
        Sincroniza os fabricantes associados a uma starship.
        """
        manufacturers = manufacturer_data.split(", ")
        for manufacturer_name in manufacturers:
            manufacturer = Manufacturer.query.filter_by(name=manufacturer_name).first()
            if not manufacturer:
                manufacturer = Manufacturer(name=manufacturer_name)
                db.session.add(manufacturer)

            # Criar relação entre starship e manufacturer
            if not StarshipManufacturer.query.filter_by(
                    starship_id=starship.id, manufacturer_id=manufacturer.id
            ).first():
                relation = StarshipManufacturer(starship_id=starship.id, manufacturer_id=manufacturer.id)
                db.session.add(relation)
