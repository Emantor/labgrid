from urllib.parse import urlsplit, urlunsplit

from .ssh import sshmanager

from ..resource.common import NetworkResource, Resource

__all__ = ['proxymanager']


class ProxyManager:
    """The ProxyManager class is only used inside labgrid.util.proxy (similar
    to a singleton), don't instanciate this class, use the exported
    proxymanager instead."""
    force_proxy = False

    @classmethod
    def force_proxy(cls, force_proxy):
        cls.force_proxy = cls.force_proxy or force_proxy

    @classmethod
    def get_ssh_prefix(cls, res, force_proxy=False):
        assert isinstance(res, Resource)

        host = res.host
        if hasattr(res, 'extra'):
            proxy_required = res.extra.get('proxy_required')
            proxy = res.extra.get('proxy')
        else:
            proxy_required = None
            proxy = None

        if proxy_required or cls.force_proxy or force_proxy:
            host = proxy

        conn = sshmanager.get(proxy)
        return conn.get_prefix()

    @classmethod
    def get_host_and_port(cls, res, force_proxy=False):
        """ get host and port for a proxy connection from a Resource

        Args:
            res (Resource): The resource to retrieve the proxy for
            force_proxy (:obj:`bool`, optional): whether to always proxy the
                connection, defaults to False

        Returns:
            (host, port) host and port for the proxy connection

        Raises:
            ExecutionError: if the SSH connection/forwarding fails
        """
        assert isinstance(res, Resource)

        if not hasattr(res, 'extra'):
            return res.host, res.port

        # res must be a NetworkResource now
        assert isinstance(res, NetworkResource)

        proxy_required = res.extra.get('proxy_required')
        proxy = res.extra.get('proxy')
        if proxy_required is None or proxy is None:
            return res.host, res.port

        if proxy_required or cls.force_proxy or force_proxy:
            port = sshmanager.request_forward(proxy, res.host, res.port)
            host = 'localhost'
            return host, port
        return res.host, res.port

    @classmethod
    def get_url(cls, url, force_proxy=False):
        assert isinstance(url, str)

        s = urlsplit(url)

        if not (cls.force_proxy or force_proxy):
            return urlunsplit(s)

        port = sshmanager.request_forward(s.hostname, '127.0.0.1', s.port)
        s = s._replace(netloc="{}:{}".format('127.0.0.1', port))
        return urlunsplit(s)


proxymanager = ProxyManager()
