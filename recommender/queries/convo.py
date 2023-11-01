from django.conf import settings
from chancog.sagenerate.cosmos import CosmosHandler

cosmos_key = settings.COSMOS_KEY
cosmos_url = settings.COSMOS_URL
cosmos_db_name = settings.COSMOS_DB_NAME


class Convo():

    def __init__(self, convo_id):
        self.convo_id = convo_id
        self.cosmos_handler = CosmosHandler(
            cosmos_key=cosmos_key,
            cosmos_url=cosmos_url,
            cosmos_db_name=cosmos_db_name)

    def is_exist(self):
        is_exists, diagnostics = self.cosmos_handler.does_convo_exist(self.convo_id)
        return is_exists

    def create(self):
        is_created, diagnostics = self.cosmos_handler.add_convo(self.convo_id)
        return is_created

    def get(self):
        convo, diagnostics = self.cosmos_handler.get_convo(self.convo_id)
        return convo

    def create_snippets(self, snippets, suggestion_bundles=None):
        is_created, diagnostics = self.cosmos_handler.add_snippets(self.convo_id, snippets, suggestion_bundles)
        return is_created




# import uuid
# from queries.convo import Convo
# convo_id = str(uuid.uuid4())
# Convo(convo_id=convo_id).create()
