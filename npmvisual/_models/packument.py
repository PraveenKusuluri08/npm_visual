import warnings
from typing import Annotated, Any, Union

from pydantic import BaseModel, Field, StringConstraints
from pydantic.config import ConfigDict
from pydantic.functional_validators import model_validator


class Repository(BaseModel):
    directory: str | None = None
    type: str | None = None
    url: str


class Funding(BaseModel):
    type: str
    url: str


class Overrides(BaseModel):
    # This needs recursion, hence using a forward reference
    __root__: dict[str, Union[str, "Overrides"]]

    class Config:
        arbitrary_types_allowed = True


class PeerDependencyMeta(BaseModel):
    optional: bool


class DeprecatedLicense(BaseModel):
    type: str
    url: str


# Signature (used in dist)
class Signature(BaseModel):
    sig: str
    keyid: str


# Dist (properties of Packument.versions)
class Dist(BaseModel):
    # deprecated?  (ref: found in uuid@0.0.2)
    bin: dict[str, dict[str, str]] | None = (
        None  # A dictionary for `shasum` and `tarball`
    )

    # the number of files in the tarball. this is on most packages published >= 2018
    fileCount: int | None = None

    # subresource integrity string! `npm view ssri`
    # https://w3c.github.io/webappsec-subresource-integrity/
    integrity: str | None = None

    # PGP signature for the tarball
    npm_signature: str | None = Field(None, alias="npm-signature")

    # the sha1 sum of the tarball
    shasum: str

    # Out-of-date blog post about this, below. (Says this is "npm-signature", but
    # that's not what the registry provides).
    # https://blog.npmjs.org/post/172999548390/new-pgp-machinery
    signatures: list[Signature]

    # the url to the tarball for the package version
    tarball: str

    # the unpacked size of the files in the tarball. >= 2018
    unpackedSize: int | None = None


# DevEngineDependency (used in DevEngines)
class DevEngineDependency(BaseModel):
    name: str
    version: str | None = None
    onFail: (
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True,
                pattern=r"^(ignore|warn|error|download)$",  # Regex pattern constraint
            ),
        ]
        | None
    ) = "warn"


class DevEngines(BaseModel):
    os: DevEngineDependency | list[DevEngineDependency] | None = None
    cpu: DevEngineDependency | list[DevEngineDependency] | None = None
    libc: DevEngineDependency | list[DevEngineDependency] | None = None
    runtime: DevEngineDependency | list[DevEngineDependency] | None = None
    packageManager: DevEngineDependency | list[DevEngineDependency] | None = None


class Bugs(BaseModel):
    email: str | None = None
    url: str | None = None


class Contact(BaseModel):
    name: str
    email: str | None = None
    url: str | None = None


class PackageJSON(BaseModel):
    model_config = ConfigDict(extra="allow")  # Allow extra fields

    # Required Fields
    name: str
    version: str

    # Optional Fields
    author: Contact | str | None = None
    bin: dict[str, str] | None = None
    browser: dict[str, str] | str | None = None
    bugs: Bugs | str | None = None
    bundledDependencies: list[str] | bool | None = None
    bundleDependencies: list[str] | bool | None = None
    config: dict[str, Any] | None = None
    contributors: list[Contact | str] | None = None
    cpu: list[str] | None = None
    dependencies: dict[str, str] | None = None
    description: str | None = None
    devDependencies: dict[str, str] | None = None
    devEngines: DevEngines | None = None
    directories: dict[str, str] | None = None
    engines: dict[str, str] | None = None
    files: list[str] | None = None
    funding: Funding | str | list[Funding | str] | None = None
    homepage: str | None = None
    keywords: list[str] | None = None
    license: str | None = None
    licenses: DeprecatedLicense | list[DeprecatedLicense] | None = None
    main: str | None = None
    man: str | list[str] | None = None
    optionalDependencies: dict[str, str] | None = None
    os: list[str] | None = None
    overrides: Overrides | None = None
    peerDependencies: dict[str, str] | None = None
    peerDependenciesMeta: dict[str, PeerDependencyMeta] | None = None
    private: bool | None = None
    publishConfig: dict[str, Any] | None = None
    repository: Repository | str | None = None
    scripts: dict[str, str] | None = None
    # https://www.typescriptlang.org/docs/handbook/declaration-files/dts-from-js.html#editing-the-packagejson
    types: str | None = None
    workspaces: list[str] | dict[str, str] | None = None

    @model_validator(mode="before")
    def detect_extra_fields(cls, values):
        # Extract the defined field names from the class
        defined_fields = set(cls.__annotations__.keys())
        input_fields = set(values.keys())

        # Detect extra fields
        extra_fields = input_fields - defined_fields

        if extra_fields:
            # Issue a warning for extra fields
            warnings.warn(
                f"Extra fields detected: {', '.join(extra_fields)}",
                UserWarning,
                stacklevel=2,
            )

        return values


class PackumentVersion(PackageJSON):
    _id: str
    _npmVersion: str
    dist: Dist

    _hasShrinkwrap: bool | None = None
    _nodeVersion: str | None = None
    _npmUser: Contact | None = None
    gitHead: str | None = None
    author: Contact | None = None  # type: ignore[reportIncompatibleVariableOverride]
    bugs: Bugs | None = None  # type: ignore[reportIncompatibleVariableOverride]
    contributors: list[Contact] | None = None  # type: ignore[reportIncompatibleVariableOverride]
    maintainers: list[Contact] | None = None
    readme: str | None = None
    readmeFilename: str | None = None
    repository: Repository | None = None  # type: ignore[reportIncompatibleVariableOverride]
    deprecated: str | None = None


# Packument (root model for npm metadata)
class Packument(BaseModel):
    _id: str
    _rev: str
    time: dict[str, str]  # modified and created can be required, other fields allowed
    versions: dict[str, PackumentVersion]

    _cached: bool | None = None
    dist_tags: dict[str, str | None] = Field(
        ..., alias="dist-tags"
    )  # dist-tags can include 'latest'
    # Users are represented as a dict with string keys and `True` values
    users: dict[str, bool] | None = None

    # Hoisted fields from PackumentVersion
    name: str
    gitHead: str | None = None
    author: Contact | None = None  # type: ignore[reportIncompatibleVariableOverride]
    bugs: Bugs | None = None  # type: ignore[reportIncompatibleVariableOverride]
    contributors: list[Contact] | None = None  # type: ignore[reportIncompatibleVariableOverride]
    maintainers: list[Contact] | None = None
    readme: str | None = None
    readmeFilename: str | None = None
    repository: Repository | None = None  # type: ignore[reportIncompatibleVariableOverride]
    description: str | None = None
    homepage: str | None = None
    keywords: list[str] | None = None
    license: str | None = None


# ManifestVersion (same structure as PackumentVersion, but trimmed)
class ManifestVersion(PackumentVersion):
    _hasShrinkwrap: bool | None = None
    bin: dict[str, str] | None = None
    bundledDependencies: list[str] | bool | None = None
    bundleDependencies: list[str] | bool | None = None
    dependencies: dict[str, str] | None = None
    deprecated: str | None = None
    devDependencies: dict[str, str] | None = None
    directories: dict[str, str] | None = None
    dist: Dist
    engines: dict[str, str] | None = None
    name: str
    optionalDependencies: dict[str, str] | None = None
    peerDependencies: dict[str, str] | None = None
    version: str


"""
abbreviated metadata format (aka corgi)

https://github.com/npm/registry/blob/master/docs/responses/package-metadata.md#abbreviated-metadata-format
returned from registry requests with accept header values conianing
`application/vnd.npm.install-v1+json`

Manifest (root metadata with versions)
"""


class Manifest(BaseModel):
    modified: str
    versions: dict[str, ManifestVersion]
    _cached: bool | None = None
    name: str
    dist_tags: dict[str, str | None] = Field(
        ..., alias="dist-tags"
    )  # dist-tags (can include 'latest')


# from __future__ import annotations
#
# import json
# from typing import Any
#
# from pydantic import BaseModel, Field, ValidationError
# from pydantic.config import ConfigDict
#
# from npmvisual.models import Dependency
#
#
# class Time(BaseModel):
#     model_config = ConfigDict(extra="allow")
#
#     modified: str
#     created: str
#
#     class Config:
#         # Allows arbitrary additional fields of type string
#         # In Pydantic v2, we use `extra` in the model config
#         extra = "allow"
#
#
# class Dist_Tags(BaseModel):
#     latest: str
#     next: str | None = None
#
#
# class Packument(BaseModel):
#     model_config = ConfigDict(extra="ignore")
#
#     _id: str
#     _rev: str
#     dist_tags: Dist_Tags
#
#     _cached: bool | None
#     dependencies: list[Dependency]
#     latest_version: str
#     time: Time
#
#     # mapping user name string keys to True (i don't know why, but the api says these will
#     # always be true. see the typescript npm types)
#     users: dict[str, bool] | None = None
#
#
# #
# # export type Packument = {
# #   _cached?: boolean;
# #   _id: string;
# #   _rev: string;
# #   "dist-tags": { latest?: string } & Record<string, string>;
# #   time: { modified: string; created: string } & Record<string, string>;
# #   users?: Record<string, true>;
# #   versions: Record<string, PackumentVersion>;
# #
# #   // these fields are hoisted from the latest PackumentVersion
# # }
