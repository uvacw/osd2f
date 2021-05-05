"""Microsoft MSAL authentication wrapper

Contains the route-wrapper for `auth()` paths configured to use
Microsoft Authentication Library.

Expects a JSON configuration set as a single string in the `MSAL_CONFIG` field.
"""

import os

import msal

from quart import redirect, request, session

from ..database import insert_log
from ..definitions import MSALConfiguration


async def microsoft_msal_authentication(func, *args, **kwargs):

    msal_auth = os.environ.get("MSAL_CONFIG")
    config = MSALConfiguration.parse_raw(msal_auth)

    authorizer = msal.ConfidentialClientApplication(
        config.client_id,
        authority=config.authority,
        client_credential=config.secret,
    )
    accepted_users = [u.strip() for u in config.allowed_users.split(";")]

    # new user
    if not session.get("user") and not session.get("flow"):
        flow = authorizer.initiate_auth_code_flow(
            config.scope,
            redirect_uri=config.redirect_url,
        )
        session["flow"] = flow
        return redirect(flow["auth_uri"])

    # returning from microsoft authentication portal
    elif session.get("flow"):
        try:
            token = authorizer.acquire_token_by_auth_code_flow(
                session.get("flow"), request.args
            )
        except ValueError:
            await insert_log(
                "server", "WARN", "unable to acquire token for authentication"
            )
            session.clear()
            return 'Something went wrong, please <a href="/researcher"> try again </a>'
        session.pop("flow")
        if "id_token_claims" not in token:
            await insert_log(
                "server",
                "WARN",
                "MSAL response did not contain `id_token_claims`, this may indicate that the configuration must be checked by an organizational administrator or is otherwise incomplete.",
            )
            return (
                "This app is unable to verify your identity due to lacking rigths.",
                500,
            )
        if token["id_token_claims"].get("preferred_username") in accepted_users:
            session["user"] = token["id_token_claims"].get("preferred_username")
            return redirect(request.url)
        else:
            await insert_log(
                "server",
                "WARN",
                "unauthorized access attempt",
                user_agent_string=request.headers.get("User-Agent"),
            )
            return "Your account is not authorized", 403

    # with active authorized session
    elif session.get("user"):
        await insert_log(
            "server",
            "INFO",
            "download access by authorized user",
            entry={"user": session.get("user"), "path": request.url},
            user_agent_string=request.headers.get("User-Agent"),
        )
        return await func(*args, **kwargs)
    return redirect("/")
