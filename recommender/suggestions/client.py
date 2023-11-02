from django.conf import settings

from chancog.sagenerate.endpoints import process_new_user_message


def perform_search(query, convo_id):
    results = process_new_user_message(
        convo_id=convo_id,
        user_message=query,
        cosmos_handler=settings.COSMOS_HANDLER,
        oai_handler=settings.OAI_HANDLER,
        pc_handler=settings.PC_HANDLER,
        tvdb_handler=settings.TVDB_HANDLER,
        ol_handler=settings.OL_HANDLER,
        fast_dev=settings.IS_FAST_DEV
    )
    return results