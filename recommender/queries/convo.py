# from django.conf import settings
# from chancog.sagenerate.cosmos import CosmosHandler
#
#
#
#
# class Convo():
#
#     def __init__(self, convo_id):
#         self.convo_id = convo_id
#
#     def is_exist(self):
#         is_exists, diagnostics = settings.COSMOS_HANDLER.does_convo_exist(self.convo_id)
#         return is_exists
#
#     def create(self):
#         is_created, diagnostics = settings.COSMOS_HANDLER.add_convo(self.convo_id)
#         return is_created
#
#     def get(self):
#         convo, diagnostics = settings.COSMOS_HANDLER.get_convo(self.convo_id)
#         return convo
#
#     def create_snippets(self, snippets, suggestion_bundles=None):
#         is_created, diagnostics = settings.COSMOS_HANDLER.add_snippets(self.convo_id, snippets, suggestion_bundles)
#         return is_created
#
#
#
#
# # import uuid
# # from queries.convo import Convo
# # convo_id = str(uuid.uuid4())
# # Convo(convo_id=convo_id).create()