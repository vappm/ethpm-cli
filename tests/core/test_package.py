import pytest

from ethpm_cli._utils.ipfs import get_ipfs_backend
from ethpm_cli.package import Package


@pytest.fixture
def ipfs_backend():
    return get_ipfs_backend()


def test_package(owned_pkg_data, ipfs_backend):
    package = Package(owned_pkg_data["ipfs_uri"], None, ipfs_backend)

    assert package.alias == "owned"
    assert package.target_uri == owned_pkg_data["ipfs_uri"]
    assert package.manifest_uri == owned_pkg_data["ipfs_uri"]
    assert package.registry_address is None
    assert package.resolved_content_hash == owned_pkg_data["content_hash"]
    assert package.raw_manifest == owned_pkg_data["raw_manifest"]
    assert package.manifest == owned_pkg_data["manifest"]


def test_package_with_alias(owned_pkg_data, ipfs_backend):
    package = Package(owned_pkg_data["ipfs_uri"], "owned-alias", ipfs_backend)

    assert package.alias == "owned-alias"
    assert package.target_uri == owned_pkg_data["ipfs_uri"]
    assert package.manifest_uri == owned_pkg_data["ipfs_uri"]
    assert package.registry_address is None
    assert package.resolved_content_hash == owned_pkg_data["content_hash"]
    assert package.raw_manifest == owned_pkg_data["raw_manifest"]
    assert package.manifest == owned_pkg_data["manifest"]


def test_package_with_registry_uri(owned_pkg_data, ipfs_backend):
    package = Package(owned_pkg_data["registry_uri"], None, ipfs_backend)

    assert package.alias == "owned"
    assert package.target_uri == owned_pkg_data["registry_uri"]
    assert package.manifest_uri == owned_pkg_data["ipfs_uri"]
    assert package.registry_address == owned_pkg_data["registry_address"]
    assert package.resolved_content_hash == owned_pkg_data["content_hash"]
    assert package.raw_manifest == owned_pkg_data["raw_manifest"]
    assert package.manifest == owned_pkg_data["manifest"]


def test_package_with_registry_uri_with_alias(owned_pkg_data, ipfs_backend):
    package = Package(owned_pkg_data["registry_uri"], "owned-alias", ipfs_backend)

    assert package.alias == "owned-alias"
    assert package.target_uri == owned_pkg_data["registry_uri"]
    assert package.manifest_uri == owned_pkg_data["ipfs_uri"]
    assert package.registry_address == owned_pkg_data["registry_address"]
    assert package.resolved_content_hash == owned_pkg_data["content_hash"]
    assert package.raw_manifest == owned_pkg_data["raw_manifest"]
    assert package.manifest == owned_pkg_data["manifest"]
