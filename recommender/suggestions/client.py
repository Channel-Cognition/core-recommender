from django.conf import settings

from chancog.sagenerate.processing import process_new_user_message


def perform_search(query, convo_id):
    response = {"MESSAGE_STATUS": "SUCCESS",
                 "MESSAGE_DATA": ""}
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
    get_error = results.get("error", None)
    if get_error is not None:
        response["MESSAGE_STATUS"] = "FAILED"
        response["MESSAGE_DATA"] = get_error
        return response
    response["MESSAGE_DATA"] = results
    return response
