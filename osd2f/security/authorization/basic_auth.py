import os

from quart import Response, redirect, request, session

from ..authorization import USER_FIELD
from ...database import insert_log


async def basic_authentication(func, *args, **kwargs):

    # with active authorized session
    if session.get(USER_FIELD):
        await insert_log(
            "server",
            "INFO",
            "download access by authorized user",
            entry={USER_FIELD: session.get(USER_FIELD), "path": request.url},
            user_agent_string=request.headers.get("User-Agent"),
        )
        return await func(*args, **kwargs)

    if not request.path.endswith("/login"):
        session["CALLBACK"] = request.url
        return redirect("/login")

    user, passw = os.environ["OSD2F_BASIC_AUTH"].split(";")

    ra = request.authorization

    if not ra:
        return Response(
            "", status=401, headers={"WWW-Authenticate": "Basic realm='data-donation'"}
        )

    authenticated = (
        ra and ra.type == "basic" and ra.username == user and ra.password == passw
    )

    redirect_target = session.pop("CALLBACK", "/")

    if authenticated:
        session[USER_FIELD] = f"{user}"
        return redirect(redirect_target)

    return redirect("/")
