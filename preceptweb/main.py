'''
Module      : Main 
Description : The main entry point for the program.
Copyright   : (c) Bernie Pope, 2017 
License     : MIT 
Maintainer  : bjpope@unimelb.edu.au
Portability : POSIX

Generate the PRECEPT website
'''

from argparse import ArgumentParser
import sys
import logging
import pkg_resources
import os
from jinja2 import Environment, FileSystemLoader
import yaml


EXIT_FILE_IO_ERROR = 1
EXIT_COMMAND_LINE_ERROR = 2
DEFAULT_VERBOSE = False
DEFAULT_TEMPLATES_DIR = 'templates' 
DEFAULT_OUTPUT_DIR = 'docs' 
PROGRAM_NAME = "preceptweb"
# Number of latest publications to show on index.html
MAX_LATEST_PUBLICATIONS_PRESENTATIONS = 3
# Number of latest activities to show on index.html
MAX_LATEST_ACTIVITIES = 4


try:
    PROGRAM_VERSION = pkg_resources.require(PROGRAM_NAME)[0].version
except pkg_resources.DistributionNotFound:
    PROGRAM_VERSION = "undefined_version"


def exit_with_error(message, exit_status):
    '''Print an error message to stderr, prefixed by the program name and 'ERROR'.
    Then exit program with supplied exit status.

    Arguments:
        message: an error message as a string.
        exit_status: a positive integer representing the exit status of the
            program.
    '''
    logging.error(message)
    print("{} ERROR: {}, exiting".format(PROGRAM_NAME, message), file=sys.stderr)
    sys.exit(exit_status)


def parse_args():
    '''Parse command line arguments.
    Returns Options object with command line argument values as attributes.
    Will exit the program on a command line error.
    '''
    parser = ArgumentParser(description='Generate the PRECEPT website')
    parser.add_argument('--version',
        action='version',
        version='%(prog)s ' + PROGRAM_VERSION)
    parser.add_argument('--log',
        metavar='LOG_FILE',
        type=str,
        help='record program progress in LOG_FILE')
    parser.add_argument('--templates',
        metavar='TEMPLATES_DIR',
        type=str,
        help='path to the templates directory',
        default=DEFAULT_TEMPLATES_DIR)
    parser.add_argument('--outdir',
        metavar='OUTPUT_DIR',
        type=str,
        help='path to write output HTML files',
        default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def init_logging(log_filename):
    '''If the log_filename is defined, then
    initialise the logging facility, and write log statement
    indicating the program has started, and also write out the
    command line from sys.argv

    Arguments:
        log_filename: either None to log to stderr, or the
            string name of the log file to write to
    Result:
        None
    '''
    format  = '%(asctime)s %(levelname)s - %(message)s'
    datefmt = '%m-%d-%Y %H:%M:%S'
    if log_filename is None:
        logging.basicConfig(
            level=logging.DEBUG,
            format=format,
            datefmt=datefmt)
    else:
        logging.basicConfig(filename=log_filename,
            level=logging.DEBUG,
            filemode='w',
            format=format,
            datefmt=datefmt)

    logging.info('starting: %s', ' '.join(sys.argv))


def init_jinja(options):
    return Environment(
        autoescape=False,
        loader=FileSystemLoader(options.templates),
        trim_blocks=True)
 
def render_page(options, jinja_env, template, transform, contents_filename=None):
    if contents_filename is not None:
        contents_path = os.path.join(options.templates, contents_filename)
        with open(contents_path) as contents_file:
            contents = yaml.load(contents_file, Loader=yaml.FullLoader)
    else:
        contents = {}
    contents = transform(contents)
    html = jinja_env.get_template(template).render(contents=contents)
    output_filename = os.path.join(options.outdir, template)
    with open(output_filename, 'w') as output_file:
        output_file.write(html)

def latest_publications_presentations(items):
    # we assume the presentation list is kept in date sorted order in the YAML file
    # so we don't need to sort it here
    return items[:MAX_LATEST_PUBLICATIONS_PRESENTATIONS]

def render_pages(options, jinja_env):
    Template("index.html") \
        .add_content("contents", options.templates, "index.yaml") \
        .add_content("publications_presentations", options.templates, "publications_presentations.yaml", latest_publications_presentations) \
        .add_content("media_events", options.templates, "media_events.yaml", lambda xs: xs[:MAX_LATEST_ACTIVITIES]) \
        .render_page(jinja_env, options.outdir)

    Template("about.html") \
        .add_content("contents", options.templates, "about.yaml") \
        .render_page(jinja_env, options.outdir)

    Template("funding.html") \
        .add_content("contents", options.templates, "funding.yaml") \
        .render_page(jinja_env, options.outdir)

    Template("publications.html") \
        .add_content("contents", options.templates, "publications.yaml") \
        .render_page(jinja_env, options.outdir)

    Template("presentations.html") \
        .add_content("contents", options.templates, "presentations.yaml") \
        .render_page(jinja_env, options.outdir)

    Template("contact.html") \
        .add_content("contents", options.templates, "contact.yaml") \
        .render_page(jinja_env, options.outdir)

    #Template("publications_presentations.html") \
    #    .add_content("contents", options.templates, "publications_presentations.yaml") \
    #    .render_page(jinja_env, options.outdir)

    Template("team.html") \
        .add_content("contents", options.templates, "team.yaml") \
        .render_page(jinja_env, options.outdir)

    Template("media_events.html") \
        .add_content("contents", options.templates, "media_events.yaml") \
        .render_page(jinja_env, options.outdir)
    
    Template("patient_involvement.html") \
        .add_content("contents", options.templates, "patient_involvement.yaml") \
        .render_page(jinja_env, options.outdir)

    Template("collaboration.html") \
        .add_content("contents", options.templates, "collaboration.yaml") \
        .render_page(jinja_env, options.outdir)


def identity(x):
    return x

class Template(object):

    def __init__(self, html_filename):
        self.html_filename = html_filename
        self.contents = {}

    # transform is a function applied to the YAML contents after it has
    # been read from file. It allows you to do some post processing of
    # the yaml contents before using it as an input to jinja
    def add_content(self, name, template_dir, yaml_filename=None, transform=identity):
        yaml_contents = {}
        if yaml_filename is not None:
            contents_path = os.path.join(template_dir, yaml_filename)
            with open(contents_path) as contents_file:
                yaml_contents = yaml.load(contents_file, Loader=yaml.FullLoader)
        self.contents[name] = transform(yaml_contents)
        return self

    def render_page(self, jinja_env, outdir):
        jinja_template = jinja_env.get_template(self.html_filename)
        rendered_html = jinja_template.render(**self.contents)
        output_filename = os.path.join(outdir, self.html_filename)
        with open(output_filename, 'w') as output_file:
            output_file.write(rendered_html)


def make_output_dir(options):
    if not os.path.exists(options.outdir):
        logging.debug("creating output dir: %s: done", options.outdir)
        os.makedirs(options.outdir)


def main():
    "Orchestrate the execution of the program"
    options = parse_args()
    init_logging(options.log)
    jinja_env = init_jinja(options)
    make_output_dir(options)
    render_pages(options, jinja_env)
    logging.info("done: open %s/index.html to see generated website", options.outdir)


# If this script is run from the command line then call the main function.
if __name__ == '__main__':
    main()
