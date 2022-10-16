from scrapy.contracts import Contract


class UrlCustomContract(Contract):
    """Contract to set the url of the request (mandatory)
    @url_custom http://scrapy.org application/json
    """

    name = "url_custom"

    def adjust_request_args(self, args):
        args["url"] = self.args[0]
        args["headers"] = {"Accept": self.args[1]}
        return args
