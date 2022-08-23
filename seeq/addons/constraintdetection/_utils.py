import urllib
from urllib.parse import urlparse, unquote, parse_qs
import re


def get_workbook_id_from_url(url):
    '''
    This function gets the workbook ID from the url.

    Parameters
    ----------
    url: str
        The url of the current worksheet

    Returns
    -------
    workbook_id: str
        The ID of the workbook
    '''

    parsed = urllib.parse.urlparse(url)
    parsed_path_split = parsed.path.split('/')
    for i in range(len(parsed_path_split)):
        if parsed_path_split[i] == 'workbook':
            workbook_id = parsed_path_split[i + 1]

    return workbook_id

def parse_url(url):
    unquoted_url = unquote(url)
    return urlparse(unquoted_url)

def get_worksheet_url(jupyter_notebook_url):
    parsed = parse_url(jupyter_notebook_url)
    params = parse_qs(parsed.query)
    return f"{parsed.scheme}://{parsed.netloc}/workbook/{params['workbookId'][0]}/worksheet/{params['worksheetId'][0]}"

def get_workbook_worksheet_workstep_ids(url):
    parsed = parse_url(url)
    params = parse_qs(parsed.query)
    workbook_id = None
    worksheet_id = None
    workstep_id = None
    if 'workbookId' in params:
        workbook_id = params['workbookId'][0]
    if 'worksheetId' in params:
        worksheet_id = params['worksheetId'][0]
    if 'workstepId' in params:
        workstep_id = params['workstepId'][0]
    return workbook_id, worksheet_id, workstep_id

