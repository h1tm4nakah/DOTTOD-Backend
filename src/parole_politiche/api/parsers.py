from flask_restx.reqparse import RequestParser

get_exhibition_filters_req_parser = RequestParser(bundle_errors=True)
get_exhibition_filters_req_parser.add_argument("account",type=str,location="json",store_missing=False)