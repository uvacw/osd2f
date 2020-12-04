from osd2f import config

from quart import Quart, render_template

from .logger import logger

app = Quart(__name__)


@app.route("/")
async def home():
    return await render_template("home.html")


@app.route("/privacy")
async def privacy():
    return await render_template("privacy.html")


@app.route("/donate")
async def donate():
    return await render_template("donate.html")


def start(mode: str = "Testing"):
    app.config.from_object(getattr(config, mode))

    # Check to make sure the application is never in production with a vacant key
    in_production_mode = mode == "Production"
    key_is_set = app.config["SECRET_KEY"] is not None
    if in_production_mode:
        logger.info("Starting app in production mode")
        assert key_is_set, ValueError(
            "To run OSD2F in production, the `OSD2F_SECRET` environment "
            "variable MUST be set."
        )

    app.run()
