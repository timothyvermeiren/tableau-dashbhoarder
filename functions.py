# functions.py contains helper functions
import unicodedata, re, os, json
import logging
logger = logging.getLogger(__name__)

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

# Returns the _first_ matching source for the ID specified. There should be no duplicate source IDs.
def get_source_by_id(id:str, definitions:json):
    try:
        return [source for source in definitions["sources"] if source["id"] == id][0]
    except Exception as e:
        logger.error(f"Unable to find matching source for id {id} in definitions.")
        logger.error(e)
        return None