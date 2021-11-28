#!flask/bin/python
# Eclipse Public License 2.0

import json

from flask_restx import Resource

# scr API
from api.v1 import api
from core import cache, limiter
from utils import FlaskUtils
from config import ServiceDiscoeryConfig

# github
from api.models.github_model import github_model
from api.parsers.github_parser import github_argument_parser
from repos.scr_github import CrawlerGitHub

github_ns = api.namespace('crawl_github', description='Crawler GitHub')

@github_ns.route('', methods = ['GET']) # url/user
class GetGitHubRepos(Resource):
    @limiter.limit('1000/hour') 
    @cache.cached(timeout=84600, query_string=True)
    @api.expect(github_argument_parser)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    #@api.marshal_with(github_model, code=200, description='OK', as_list=True)
    def get(self):
        """
        Returns a JSON array with the repo information
        """
        # retrieve and chek arguments
        is_from_url = False
        is_from_keyword = False
        is_from_topic = False
        r_json = ""
        try:
            args = github_argument_parser.parse_args()
            from_url = args['from_url']
            from_keyword = args['from_keyword']
            from_topic = args['from_topic']
            # None
            if from_keyword is None and from_url is None and from_topic is None:
                raise Exception("ValueError")
            # Both
            if from_url and from_keyword and from_topic:
                raise Exception("ValueError")
            # Only one
            if from_url:
                is_from_url = True
            if from_keyword:
                is_from_keyword = True
            if from_topic:
                is_from_topic = True

        except Exception as e:
            #raise e
            return FlaskUtils.handle400error(github_ns, 'The providen arguments are not correct. Please, check the swagger documentation at /v1')

        # retrieve repos
        try:
            # TODO: handle more API tokens in case of limit
            github = CrawlerGitHub(ServiceDiscoeryConfig.GITHUB_ACCESS_TOKEN_1)            
            if is_from_url:                
                r = github.get_from_url(from_url)
            if is_from_keyword:                
                r = github.get_from_keywords(from_keyword)
            if is_from_topic:
                r = github.get_from_topic(from_topic)
            
            if r is None or r.empty:
                r_json = ""
            else:                
                # split records index values table columns (the default format)
                result = r.to_json(orient="records")
                r_json = json.loads(result)

        except Exception as e:
            return FlaskUtils.handle500error(github_ns)

        # if there is not repos found  r_json == "", return 404 error
        if not r_json:
            return FlaskUtils.handle404error(github_ns, 'No GitHub repos was found for the given parameters, or bad credentials')
        # TODO: Shdl we return the raw repos found or the info about them? EX: found 39 new repos, inserted into the database ok.
        return r_json