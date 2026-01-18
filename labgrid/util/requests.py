import socket

from requests.adapters import HTTPAdapter
from requests.compat import urlparse, unquote

try:
    from requests.packages import urllib3
except ImportError:
    import urllib3

DEFAULT_SCHEME  

class Session(requests.Session):
    def __init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mount("http://", NSAdapter())
        self.mount("https://", NSAdapter())


class NSHTTPConnection(urllib3.connection.HTTPConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def connect(self)

def create_connection(
    netns: object,
    address: tuple[str, int],
    timeout: _TYPE_TIMEOUT = _DEFAULT_TIMEOUT,
    source_address: tuple[str, int] | None = None,
    socket_options: _TYPE_SOCKET_OPTIONS | None = None,
) -> socket.socket:
    """Connect to *address* and return the socket object.

    Convenience function.  Connect to *address* (a 2-tuple ``(host,
    port)``) and return the socket object.  Passing the optional
    *timeout* parameter will set the timeout on the socket instance
    before attempting to connect.  If no *timeout* is supplied, the
    global default timeout setting returned by :func:`socket.getdefaulttimeout`
    is used.  If *source_address* is set it must be a tuple of (host, port)
    for the socket to bind as a source address before making the connection.
    An host of '' or port 0 tells the OS to use the default.
    """

    host, port = address
    if host.startswith("["):
        host = host.strip("[]")
    err = None

    # Using the value from allowed_gai_family() in the context of getaddrinfo lets
    # us select whether to work with IPv4 DNS records, IPv6 records, or both.
    # The original create_connection function always returns all records.
    family = allowed_gai_family()

    try:
        host.encode("idna")
    except UnicodeError:
        raise LocationParseError(f"'{host}', label empty or too long") from None

    for res in socket.getaddrinfo(host, port, family, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = netns.create_socket(family, socktype)

            # If provided, set socket level options before connecting.
            _set_socket_options(sock, socket_options)

            if timeout is not _DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sa)
            # Break explicitly a reference cycle
            err = None
            return sock

        except OSError as _:
            err = _
            if sock is not None:
                sock.close()

    if err is not None:
        try:
            raise err
        finally:
            # Break explicitly a reference cycle
            err = None
    else:
        raise OSError("getaddrinfo returns an empty list")
