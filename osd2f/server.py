from osd2f.definitions import Submission

from quart import Quart, render_template, request
from quart.json import jsonify

from osd2f import config, utils

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


@app.route("/upload")
async def upload():

    settings = utils.load_settings(force_disk=app.debug)
    return await render_template("filesubmit.html", settings=settings)


@app.route("/anonymize", methods=["POST"])
async def anonymize():
    data = await request.get_data()
    logger.debug(f"[anonymization] received: {data}")
    if len(data) == 0:
        return jsonify({"error": "no data received"}), 400

    settings = utils.load_settings(force_disk=app.debug)
    try:
        submission = Submission.parse_raw(data)
    except ValueError as e:
        logger.debug(f"[anonymization] could not parse: {e}")
        return jsonify({"error": "incorrect submission format"}), 400

    return jsonify({"error": "", "data": data})


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
