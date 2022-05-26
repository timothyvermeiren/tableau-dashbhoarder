# tableau-dashbhoarder
Hoards dashboards from Tableau Server or Tableau Cloud, to local images. In other words, kind of an automated downloader of Tableau dashboards.

## Installation

Requires Python `3.x`, probably - developed with Python `3.10.4`, so that should work.

Currently, the installation simply goes though `git clone` and Python `virtualenv`. In brief:

* Clone:  
  `git clone https://github.com/timothyvermeiren/tableau-dashbhoarder`
* Work from within that directory:  
  `cd tableau-dashbhoarder`
* Create virtualenv:
  * If `virtualenv` is not installed yet, get it first:  
    `python -m pip install virtualenv`
  * Actually create it:  
    `python -m virtualenv .venv`
* Activate the virtualenv:
  * Windows:  
    `.venv\Scripts\activate`
  * Linux:  
    `source .venv/bin/activate`
* Install required modules:  
  `python -m pip install -r requirements.txt`
* That should be it. Test according to the examples under Usage, below.

## Usage

### Running

From the command line, the tool is run "in" the virtualenv, through `main.py`, with just two arguments:
  * `--destination-path`: a default destination path (i.e. output directory) to fall back to if no path has been specified for content specifically.
  * `--definitions-file`: defines which content is to be hoarded, from where, to where. This is the key to how to tool works, explained below.

In other words, a simple example (on Windows):  
`.venv\Scripts\python.exe main.py --definitions-file .\config\definitions.json --destination-path .`

### "Definitions" and concepts

The manner in which the script will run, which content it will download, where it will be stored, etc., is referred to as the **Definitions**. These definitions are to be provided in the definitions JSON file, and the following rules and concepts apply. 

There are two components to the definitions file:
* The `sources` part, containing the references to the Tableau environment(s) from which content will be hoarded.
  * Each source has a unique `id`, which will be referred to from the next section.
  * Aside from that, the Server/Online URL, Personal Access Token, etc. are defined here.
* The `content` part, which lists what will be downloaded, as well as where and how.
  * Name and comment values are used to label the content.
  * There is a `source` field referring to the sources' `id` from above.
  * There is a `url` field that can simply be copied from the browser - a reference to the view on Tableau Server or Online. The information that's really extracted from here is the end of the base URL, usually `WorkbookName/ViewName`.
  * Finally, there is an optional `target` key to specify where the output will be written. The extension is added automatically to the `filename`. Either or both of `filename` and `path` can be left out, in which case the tool will revert to defaults.

An example definitions file is provided under [config/definitions.json.template](config/definitions.json.template).

## To do

* Implement proper credential management (through keyring, notably)
* Implement "content type" so PDF or PPT can be downloaded aside from PNG.
