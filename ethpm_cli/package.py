from collections import namedtuple
import json
from typing import Any, Dict, Iterable, Tuple  # noqa: F401
from urllib import parse

from eth_utils import to_dict, to_text
from ethpm.backends.http import GithubOverHTTPSBackend
from ethpm.backends.ipfs import BaseIPFSBackend
from ethpm.backends.registry import RegistryURIBackend
from ethpm.typing import URI, Address, Manifest  # noqa: F401
from ethpm.utils.ipfs import extract_ipfs_path_from_uri, generate_file_hash, is_ipfs_uri
from ethpm.utils.manifest_validation import (
    validate_manifest_against_schema,
    validate_manifest_deployments,
    validate_raw_manifest_format,
)
from ethpm.utils.uri import (
    is_valid_content_addressed_github_uri,
    parse_registry_uri,
    validate_blob_uri_contents,
)
from ethpm.validation import is_valid_registry_uri

from ethpm_cli.exceptions import UriNotSupportedError


class Package:
    def __init__(
        self, target_uri: URI, alias: str, ipfs_backend: BaseIPFSBackend
    ) -> None:
        self.ipfs_backend = ipfs_backend
        resolved_target_uri = resolve_target_uri(target_uri)
        self.manifest_uri: URI = resolved_target_uri.manifest_uri
        self.registry_address: Address = resolved_target_uri.registry_address

        resolved_manifest_uri = resolve_manifest_uri(
            self.manifest_uri, self.ipfs_backend
        )
        self.raw_manifest: bytes = resolved_manifest_uri.raw_manifest
        self.resolved_content_hash: str = resolved_manifest_uri.resolved_content_hash

        self.manifest: Manifest = process_and_validate_raw_manifest(self.raw_manifest)
        self.alias = alias if alias else self.manifest["package_name"]
        self.target_uri = target_uri

    @to_dict
    def generate_ethpm_lock(self) -> Iterable[Tuple[str, str]]:
        yield "resolved_uri", self.manifest_uri
        yield "resolved_content_hash", self.resolved_content_hash
        yield "target_uri", self.target_uri
        yield "registry_address", self.registry_address
        yield "alias", self.alias
        yield "resolved_version", self.manifest["version"]
        yield "resolved_package_name", self.manifest["package_name"]


ResolvedTargetURI = namedtuple(
    "ResolvedTargetURI", ["manifest_uri", "registry_address"]
)
ResolvedManifestURI = namedtuple(
    "ResolvedManifestURI", ["raw_manifest", "resolved_content_hash"]
)


def resolve_manifest_uri(uri: URI, ipfs: BaseIPFSBackend) -> ResolvedManifestURI:
    if is_valid_content_addressed_github_uri(uri):
        raw_manifest = GithubOverHTTPSBackend().fetch_uri_contents(uri)
        validate_blob_uri_contents(raw_manifest, uri)
        resolved_content_hash = parse.urlparse(uri).path.split("/")[-1]
    elif is_ipfs_uri(uri):
        raw_manifest = ipfs.fetch_uri_contents(uri)
        manifest_content_hash = extract_ipfs_path_from_uri(uri)
        resolved_content_hash = generate_file_hash(raw_manifest)
        if resolved_content_hash != manifest_content_hash:
            raise UriNotSupportedError(
                f"Contents found at {uri} resolved to the content hash {resolved_content_hash} "
                f"which don't match the uri content hash of {manifest_content_hash}."
            )
    else:
        raise UriNotSupportedError(
            f"{uri} is not supported. Currently EthPM CLI only supports "
            "IPFS & Github blob manifest uris."
        )
    return ResolvedManifestURI(raw_manifest, resolved_content_hash)


def resolve_target_uri(uri: URI) -> ResolvedTargetURI:
    if is_valid_registry_uri(uri):
        manifest_uri = RegistryURIBackend().fetch_uri_contents(uri)
        registry_address = parse_registry_uri(uri).auth
    else:
        manifest_uri = uri
        registry_address = None
    return ResolvedTargetURI(manifest_uri, registry_address)


def process_and_validate_raw_manifest(raw_manifest: bytes) -> Manifest:
    raw_manifest_text = to_text(raw_manifest).rstrip("\n")
    validate_raw_manifest_format(raw_manifest_text)
    manifest = json.loads(raw_manifest_text)
    validate_manifest_against_schema(manifest)
    validate_manifest_deployments(manifest)
    return manifest
