__author__ = 'rohe0002'

from oic.oic.message import *

ENDPOINTS = ["authorization_endpoint", "token_endpoint",
             "user_info_endpoint", "refresh_session_endpoint",
             "check_session_endpoint", "end_session_endpoint",
             "registration_endpoint"]

RESPONSE2ERROR = {
    AuthorizationResponse: [AuthorizationErrorResponse, TokenErrorResponse],
    AccessTokenResponse: [TokenErrorResponse]
}

REQUEST2ENDPOINT = {
    AuthorizationRequest: "authorization_endpoint",
    AccessTokenRequest: "token_endpoint",
    RefreshAccessTokenRequest: "token_endpoint",
    UserInfoRequest: "user_info_endpoint",
    CheckSessionRequest: "check_session_endpoint",
    EndSessionRequest: "end_session_endpoint",
    RefreshSessionRequest: "refresh_session_endpoint",
    RegistrationRequest: "registration_endpoint"
}

class Token(oauth2.Token):
    _class = AccessTokenResponse


class Grant(oauth2.Grant):
    _authz_resp = AuthorizationResponse
    _acc_resp = AccessTokenResponse
    _token_class = Token

#noinspection PyMethodOverriding
class Client(oauth2.Client):
    def __init__(self, client_id=None, cache=None, timeout=None,
                 proxy_info=None, follow_redirects=True,
                 disable_ssl_certificate_validation=False, key=None,
                 algorithm="HS256", client_secret="", client_timeout=0,
                 expires_in=0):

        if expires_in:
            client_timeout = time_sans_frac() + expires_in

        oauth2.Client.__init__(self, client_id, cache, timeout, proxy_info,
                       follow_redirects, disable_ssl_certificate_validation,
                       key, algorithm, client_secret, client_timeout)

        self.file_store = "./file/"
        self.file_uri = "http://localhost/"

        # OpenID connect specific endpoints
        for endpoint in ENDPOINTS:
            setattr(self, endpoint, "")

        self.id_token=None
        self.log = None

        self.request2endpoint = REQUEST2ENDPOINT
        self.response2error = RESPONSE2ERROR
        self.grant_class = Grant
        self.token_class = Token

    def _get_id_token(self, **kwargs):
        token = self.get_token(**kwargs)

        if token:
            return token.id_token
        else:
            return None

    def construct_AuthorizationRequest(self, cls=AuthorizationRequest,
                                       request_args=None, extra_args=None,
                                       **kwargs):

        return oauth2.Client.construct_AuthorizationRequest(self, cls,
                                                            request_args,
                                                            extra_args,
                                                            **kwargs)

    #noinspection PyUnusedLocal
    def construct_AccessTokenRequest(self, cls=AccessTokenRequest,
                                     request_args=None, extra_args=None,
                                     **kwargs):

        return oauth2.Client.construct_AccessTokenRequest(self, cls,
                                                          request_args,
                                                          extra_args, **kwargs)

    def construct_RefreshAccessTokenRequest(self,
                                            cls=RefreshAccessTokenRequest,
                                            request_args=None, extra_args=None,
                                            **kwargs):

        return oauth2.Client.construct_RefreshAccessTokenRequest(self, cls,
                                                          request_args,
                                                          extra_args, **kwargs)

    def construct_UserInfoRequest(self, cls=UserInfoRequest,
                                  request_args=None, extra_args=None, **kwargs):

        if request_args is None:
            request_args = {}

        if "access_token" in request_args:
            pass
        else:
            token = self.get_token(**kwargs)
            if token is None:
                raise Exception("No valid token available")

            request_args["access_token"] = token.access_token

        return self.construct_request(cls, request_args, extra_args)

    #noinspection PyUnusedLocal
    def construct_RegistrationRequest(self, cls=RegistrationRequest,
                                      request_args=None, extra_args=None,
                                      **kwargs):

        return self.construct_request(cls, request_args, extra_args)

    #noinspection PyUnusedLocal
    def construct_RefreshSessionRequest(self, cls=RefreshSessionRequest,
                                        request_args=None, extra_args=None,
                                        **kwargs):

        return self.construct_request(cls, request_args, extra_args)

    def _id_token_based(self, cls, request_args=None, extra_args=None,
                        **kwargs):

        if request_args is None:
            request_args = {}

        if "id_token" in request_args:
            pass
        else:
            id_token = self._get_id_token(**kwargs)
            if id_token is None:
                raise Exception("No valid id token available")

            request_args["id_token"] = id_token

        return self.construct_request(cls, request_args, extra_args)

    def construct_CheckSessionRequest(self, cls=CheckSessionRequest,
                                        request_args=None, extra_args=None,
                                        **kwargs):

        return self._id_token_based(cls, request_args, extra_args, **kwargs)

#    def construct_CheckIDRequest(self, cls=CheckIDRequest, request_args=None,
#                                 extra_args=None, **kwargs):
#
#        return self._id_token_based(cls, request_args, extra_args, **kwargs)

    def construct_EndSessionRequest(self, cls=EndSessionRequest,
                                    request_args=None, extra_args=None,
                                    **kwargs):

        if request_args is None:
            request_args = {}
            
        if "state" in kwargs:
            request_args["state"] = kwargs["state"]
        elif "state" in request_args:
            kwargs["state"] = request_args["state"]

#        if "redirect_url" not in request_args:
#            request_args["redirect_url"] = self.redirect_url
            
        return self._id_token_based(cls, request_args, extra_args, **kwargs)

    def construct_OpenIDRequest(self, cls=OpenIDRequest, request_args=None,
                                extra_args=None, **kwargs):
        if request_args is None:
            request_args = {}

        if "state" in kwargs:
            request_args["state"] = kwargs["state"]

        for prop in ["redirect_uri", "client_id", "scope", "response_type"]:
            if prop not in request_args:
                request_args[prop] = getattr(self, prop)

        return self.construct_request(cls, request_args, extra_args)

    # ------------------------------------------------------------------------

    def do_authorization_request(self, cls=AuthorizationRequest,
                                 state="", body_type="", method="GET",
                                 request_args=None, extra_args=None,
                                 http_args=None, resp_cls=None):

        return oauth2.Client.do_authorization_request(self, cls, state,
                                                      body_type, method,
                                                      request_args,
                                                      extra_args, http_args,
                                                      resp_cls)


    def do_access_token_request(self, cls=AccessTokenRequest, scope="",
                                state="", body_type="json", method="POST",
                                request_args=None, extra_args=None,
                                http_args=None, resp_cls=AccessTokenResponse,
                                token=None):

        return oauth2.Client.do_access_token_request(self, cls, scope, state,
                                                     body_type, method,
                                                     request_args, extra_args,
                                                     http_args, resp_cls)

    def do_access_token_refresh(self, cls=RefreshAccessTokenRequest,
                                state="", body_type="json", method="POST",
                                request_args=None, extra_args=None,
                                http_args=None, resp_cls=AccessTokenResponse,
                                **kwargs):

        return oauth2.Client.do_access_token_refresh(self, cls, state,
                                                     body_type, method,
                                                     request_args,
                                                     extra_args, http_args,
                                                     resp_cls, **kwargs)

#    def do_user_info_request(self, cls=UserInfoRequest, state="",
#                             body_type="json", method="POST",
#                             request_args=None, extra_args=None,
#                             http_args=None, resp_cls=UserInfoResponse,
#                             **kwargs):
#
#        token = self._get_token(state=state, **kwargs)
#        url, body, ht_args, csi = self.request_info(cls, method=method,
#                                                    request_args=request_args,
#                                                    extra_args=extra_args,
#                                                    token=token)
#
#        if http_args is None:
#            http_args = ht_args
#        else:
#            http_args.update(http_args)
#
#        return self.request_and_return(url, resp_cls, method, body,
#                                       body_type, extended=False,
#                                       state=state, http_args=http_args)

    def do_registration_request(self, cls=RegistrationRequest, scope="",
                                state="", body_type="json", method="POST",
                                request_args=None, extra_args=None,
                                http_args=None, resp_cls=RegistrationResponse):

        url, body, ht_args, csi = self.request_info(cls, method=method,
                                                    request_args=request_args,
                                                    extra_args=extra_args,
                                                    scope=scope, state=state)

        if http_args is None:
            http_args = ht_args
        else:
            http_args.update(http_args)

        return self.request_and_return(url, resp_cls, method, body,
                                       body_type, extended=False,
                                       state=state, http_args=http_args)

    def do_check_session_request(self, cls=CheckSessionRequest, scope="",
                                 state="", body_type="json", method="GET",
                                 request_args=None, extra_args=None,
                                 http_args=None,
                                 resp_cls=IdToken):

        url, body, ht_args, csi = self.request_info(cls, method=method,
                                                    request_args=request_args,
                                                    extra_args=extra_args,
                                                    scope=scope, state=state)

        if http_args is None:
            http_args = ht_args
        else:
            http_args.update(http_args)

        return self.request_and_return(url, resp_cls, method, body,
                                       body_type, extended=False,
                                       state=state, http_args=http_args)

#    def do_check_id_request(self, cls=CheckIDRequest, scope="",
#                                 state="", body_type="json", method="POST",
#                                 request_args=None, extra_args=None,
#                                 http_args=None, resp_cls=None):
#
#        url, body, ht_args, csi = self.request_info(cls, method=method,
#                                                    request_args=request_args,
#                                                    extra_args=extra_args,
#                                                    scope=scope, state=state)
#
#        if http_args is None:
#            http_args = ht_args
#        else:
#            http_args.update(http_args)
#
#        return self.request_and_return(url, resp_cls, method, body,
#                                       body_type, extended=False,
#                                       state=state, http_args=http_args)

    def do_end_session_request(self, cls=EndSessionRequest, scope="",
                                 state="", body_type="", method="GET",
                                 request_args=None, extra_args=None,
                                 http_args=None, resp_cls=None):

        url, body, ht_args, csi = self.request_info(cls, method=method,
                                                    request_args=request_args,
                                                    extra_args=extra_args,
                                                    scope=scope, state=state)

        if http_args is None:
            http_args = ht_args
        else:
            http_args.update(http_args)

        return self.request_and_return(url, resp_cls, method, body,
                                       body_type, extended=False,
                                       state=state, http_args=http_args)

#    def do_open_id_request(self, cls=OpenIDRequest, scope="",
#                                 state="", body_type="json", method="GET",
#                                 request_args=None, extra_args=None,
#                                 http_args=None,
#                                 resp_cls=AuthorizationResponse):
#
#        url, body, ht_args, csi = self.request_info(cls, method=method,
#                                                    request_args=request_args,
#                                                    extra_args=extra_args,
#                                                    scope=scope, state=state)
#
#        if http_args is None:
#            http_args = ht_args
#        else:
#            http_args.update(http_args)
#
#        return self.request_and_return(url, resp_cls, method, body,
#                                       body_type, extended=False,
#                                       state=state, http_args=http_args)

    def get_or_post(self, uri, method, req, **kwargs):
        if method == "GET":
            path = uri + '?' + req.get_urlencoded()
            body = None
        elif method == "POST":
            path = uri
            body = req.get_urlencoded()
            header_ext = {"content-type": "application/x-www-form-urlencoded"}
            if "headers" in kwargs.keys():
                kwargs["headers"].update(header_ext)
            else:
                kwargs["headers"] = header_ext
        else:
            raise Exception("Unsupported HTTP method: '%s'" % method)

        return path, body, kwargs

    def user_info_request(self, method="GET", state="", scope="", **kwargs):
        uir = UserInfoRequest()
        token = self.grant[state].get_token(scope)

        if token.is_valid():
            uir.access_token = token.access_token
        else:
            # raise oauth2.OldAccessToken
            if self.log:
                self.log.info("do access token refresh")
            try:
                self.do_access_token_refresh(token=token)
                token = self.grant[state].get_token(scope)
                uir.access_token = token.access_token
            except Exception:
                raise

        try:
            uir.schema = kwargs["schema"]
        except KeyError:
            pass

        uri = self._endpoint("user_info_endpoint", **kwargs)

        path, body, kwargs = self.get_or_post(uri, method, uir, **kwargs)

        h_args = dict([(k, v) for k,v in kwargs.items() if k in HTTP_ARGS])

        return path, body, method, h_args

    def do_user_info_request(self, method="POST", state="", scope="openid",
                             schema="openid", **kwargs):

        kwargs["schema"] = schema
        path, body, method, h_args = self.user_info_request(method, state,
                                                           scope, **kwargs)

        try:
            response, content = self.http.request(path, method, body, **h_args)
        except oauth2.MissingRequiredAttribute:
            raise

        if response.status == 200:
            assert "application/json" in response["content-type"]
        elif response.status == 500:
            raise Exception("ERROR: Something went wrong: %s" % content)
        else:
            raise Exception("ERROR: Something went wrong [%s]" % response.status)

        return UserInfoResponse.set_json(txt=content, extended=True)


#noinspection PyMethodOverriding
class Server(oauth2.Server):
    def __init__(self, jwt_keys=None):
        oauth2.Server.__init__(self)

        self.jwt_keys = jwt_keys or {}

    def _parse_urlencoded(self, url=None, query=None):
        if url:
            parts = urlparse.urlparse(url)
            scheme, netloc, path, params, query, fragment = parts[:6]

        return urlparse.parse_qs(query)

    def parse_token_request(self, cls=AccessTokenRequest, body=None,
                            extended=False):
        return oauth2.Server.parse_token_request(self, cls, body, extended)

    def parse_authorization_request(self, rcls=AuthorizationRequest,
                                    url=None, query=None, extended=False):
        return oauth2.Server.parse_authorization_request(self, rcls, url,
                                                         query, extended)

    def parse_jwt_request(self, rcls=AuthorizationRequest, txt="", key="",
                          verify=True, extended=False):

        return oauth2.Server.parse_jwt_request(self, rcls, txt, key, verify,
                                               extended)

    def parse_refresh_token_request(self, cls=RefreshAccessTokenRequest,
                                    body=None, extended=False):
        return oauth2.Server.parse_refresh_token_request(self, cls, body,
                                                         extended)

    def _deser_id_token(self, str=""):
        if not str:
            return None
        
        # have to start decoding the jwt without verifying in order to find
        # out which key to verify the JWT signature with
        info = json.loads(jwt.decode(str, verify=False))

        # in there there should be information about the client_id
        # Use that to find the key and do the signature verify

        return IdToken.set_jwt(str, key=self.jwt_keys[info["iss"]])

    def parse_check_session_request(self, url=None, query=None):
        """

        """
        param = self._parse_urlencoded(url, query)
        assert "id_token" in param # ignore the rest
        return self._deser_id_token(param["id_token"][0])

    def _parse_request(self, cls, data, format, extended):
        if format == "json":
            request = cls.set_json(data, extended)
        elif format == "urlencoded":
            if '?' in data:
                parts = urlparse.urlparse(data)
                scheme, netloc, path, params, query, fragment = parts[:6]
            else:
                query = data
            request = cls.set_urlencoded(query, extended)
        else:
            raise Exception("Unknown package format: '%s'" %  format)

        request.verify()
        return request
    
    def parse_open_id_request(self, data, format="urlencoded", extended=False):
        return self._parse_request(OpenIDRequest, data, format, extended)

    def parse_user_info_request(self, data, format="urlencoded", extended=False):
        return self._parse_request(UserInfoRequest, data, format, extended)

    def parse_refresh_session_request(self, url=None, query=None,
                                      extended=False):
        if url:
            parts = urlparse.urlparse(url)
            scheme, netloc, path, params, query, fragment = parts[:6]

        return RefreshSessionRequest.set_urlencoded(query, extended)

    def parse_registration_request(self, data, format="urlencoded",
                                   extended=True):
        return self._parse_request(RegistrationRequest, data, format, extended)

    def parse_end_session_request(self, query, extended=True):
        esr = EndSessionRequest.set_urlencoded(query, extended)
        # if there is a id_token in there it is as a string
        esr.id_token = self._deser_id_token(esr.id_token)
        return esr
    

