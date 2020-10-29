#
# Conveniences to create consistent callback handlers for endpoints


class CB(object):
    @classmethod
    def _status(klass, response, allow_404=True):
        # status checking
        if 400 <= response.code < 500:
            if response.code == 400:
                raise exceptions.BadRequest("%d %s" % (response.code, response.body))
            elif response.code == 401:
                raise exceptions.ACLDisabled(response.body)
            elif response.code == 403:
                raise exceptoions.ACLPermissionDenied(response.body)
            elif response.code == 404:
                if not allow_404:
                    raise exceptions.NotFound(response.body)
            else:
                raise exceptions.ClientError("%d %s" % (response.code, response.body))
        elif 500 <= response.code < 600:
            raise exceptions.ConsulException("%d %s" % (response.code, response.body))

    @classmethod
    def bool(klass):
        # returns True on successful response
        def cb(response):
            CB._status(response)
            return response.code == 200

        return cb

    @classmethod
    def json(
        klass,
        map=None,
        allow_404=True,
        one=False,
        decode=False,
        is_id=False,
        index=False,
    ):
        """
        *map* is a function to apply to the final result.

        *allow_404* if set, None will be returned on 404, instead of raising
        NotFound.

        *index* if set, a tuple of index, data will be returned.

        *one* returns only the first item of the list of items. empty lists are
        coerced to None.

        *decode* if specified this key will be base64 decoded.

        *is_id* only the 'ID' field of the json object will be returned.
        """

        def cb(response):
            CB._status(response, allow_404=allow_404)
            if response.code == 404:
                return response.headers.get("X-Consul-Index"), None

            data = json.loads(response.body)

            if decode:
                for item in data:
                    if item.get(decode) is not None:
                        item[decode] = base64.b64decode(item[decode])
            if is_id:
                data = data["ID"]
            if one:
                if not data:
                    data = None
                if data is not None:
                    data = data[0]
            if map:
                data = map(data)
            if index:
                return response.headers["X-Consul-Index"], data
            return data

        return cb

    @classmethod
    def binary(klass):
        """
        This method simply returns response body, usefull for snapshot
        """

        def cb(response):
            CB._status(response)
            return response.content

        return cb
