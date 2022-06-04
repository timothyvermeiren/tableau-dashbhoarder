import tableauserverclient as TSC
import argparse # to parse additional arguments and the mode we'll use
# import configparser
import logging
import logging.handlers # For RotatingFileHandler
import os, sys, datetime, re, json, time
from functions import slugify, get_source_by_id

# First thing, logs directory
if not os.path.exists("logs"):
    os.makedirs("logs")

# Timing
start_time = time.time()
start_datetime = datetime.datetime.utcnow()

##### Logging
logger = logging.getLogger() # Root logger
log_file_name = "logs" + os.sep + "tableau_dashbhoarder.log"
log_file_handler = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=5000000, backupCount=5)
log_console_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s")
log_file_handler.setFormatter(log_formatter)
log_console_handler.setFormatter(log_formatter)
logger.setLevel(logging.INFO)
logger.addHandler(log_file_handler)
logger.addHandler(log_console_handler)

logger.info("Tableau Dashbhoarder v1.0")

# Parse arguments first
parser = argparse.ArgumentParser(prog="tableau-dashbhoarder", description="Hoard dashboards to local images with this simple tool.")
# Operational arguments
parser.add_argument("--destination-path", "-d", dest="destination_path", required=False, type=str, help="The Default location images will be stored in when none is specified at the content level. Defaults to the current working directory.")
parser.add_argument("--definitions-file", "-c", dest="definitions_file", required=True, type=str, help="The definitions of the content that will be hoarded from specific sources, in json format. Refer to the template or the documentation for examples and structure.")

args = parser.parse_args()
if args.destination_path is None:
    # Working dir
    destination_path = "." + os.sep
else:
    destination_path = args.destination_path

# Create the local destination folder, if it doesn't exist
if not os.path.exists(destination_path):
    os.makedirs(destination_path)

logger.info(f"Destination path: { args.destination_path }")

# Pick up the definitions file:
try:
    with open(args.definitions_file, "r") as f:
        definitions = json.load(f)
except Exception as e:
    logger.error(f"Unable to load definitions from {args.definitions_file} - exiting.")
    logger.error(e)
    exit(1)

##### Get to work

# Sort and group content per server, so we can log in and fetch views only once.
for source in definitions["sources"]:
    source["actions"] = []
    for content in definitions["content"]:
        if content["source"] == source["id"]:
            source["actions"].append(content)

# Then go through the sorted, grouped content which is actually sources > content now

for source in definitions["sources"]:
    if len(source.get("actions", [])) == 0:
        logger.warning(f"Source: \"{ source['server'] }\" has no matching content, skipping source.")
    else:
        # Log in to the source
        logger.info(f"Handling source: \"{ source['server'] }\"")
        ts_site = "" if source["site"] == "Default" else source["site"] # Default site is "" for the REST API
        logger.info(f"Signing in to Tableau Server/Cloud: {source['server']} (site \"{ts_site}\").")
        ts_auth = TSC.PersonalAccessTokenAuth(token_name=source["patName"], personal_access_token=source["patSecret"], site_id=ts_site)
        tableau_server_tsc = TSC.Server(source["server"])
        tableau_server_tsc.version = source["apiVersion"] # Needed somewhow because otherwise it aims for a version way too low
        # Custom Server Certificates
        # if "ssl_certificates" in config["tableau_server"]:
            # tableau_server_tsc.add_http_options({ "verify": config["tableau_server"]["ssl_certificates"] })
        try:
            tableau_server_tsc.auth.sign_in_with_personal_access_token(ts_auth)
            logger.info(f"Getting all views from URL: { content['url'] }")
            ts_all_views = list(TSC.Pager(tableau_server_tsc.views))
        
            # Go through source's content
            for content in source["actions"]:

                try:
                    logger.info(f"Handling content: \"{ content.get('name', 'Untitled') }\". Source is \"{ content['url'] }\"")
                    
                    # Match, extract, replace with the expected pattern found in the TSC view content_url
                    matching_content_url = re.match(pattern=r".*\/views\/([\w\d\-]+\/[\w\d\-]+)", string=content["url"]).group(1).replace("/", "/sheets/")
                    ts_view = [view for view in ts_all_views if view.content_url == matching_content_url][0]

                    # Get the view image
                    image_req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High, maxage=1)
                    tableau_server_tsc.views.populate_image(ts_view, image_req_option)

                    # Determine output based on what is provided, which is a bit flexible
                    # The path specified at the content level, or otherwise the default from args.
                    image_path = content.get("destination", {}).get("path", destination_path) # Should take care of testing if the value is provided too.
                    image_filename = content.get("destination", {}).get("filename", slugify(content["name"])) + ".png"
                    image_output = os.path.join(image_path, image_filename)
                    # Let's be helpful
                    if not os.path.exists(image_path):
                        os.makedirs(image_path)

                    try:
                        with open(image_output, "wb") as image_file:
                            image_file.write(ts_view.image)
                    except Exception as e:
                        logger.error(f"Failed to write image to { image_output }")
                
                except Exception as e: # Failed to get image
                    logger.warning("An error occurred processing this content. Skipping.")
                    logger.warning(e)
        
        except Exception as e: # Failed to sign in 
            logger.error("Failed to sign in to this Tableau instance. Skipping.")
            logger.error(e)

        # Sign out
        logger.info("Signing out of this Tableau instance.")
        tableau_server_tsc.auth.sign_out()
        

# Timing
end_time = time.time()
execution_time = end_time - start_time
logger.info(f"Execution took { execution_time } seconds. We're done!")