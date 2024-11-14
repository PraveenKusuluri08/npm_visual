from typing import Annotated, Any, Union
from pydantic.types import Discriminator, Tag
from typing_extensions import TypedDict

from flask import current_app as app
from pydantic import RootModel, BaseModel, Field, StringConstraints, ValidationError
from pydantic.config import ConfigDict
from pydantic.functional_validators import model_validator

from npmvisual._models.ns_base_model import NSPrettyPrintable


class Repository(BaseModel, NSPrettyPrintable):
    directory: str | None = None
    repository_type: str | None = Field(None, alias="type")
    url: str | None = None  # Nick added None to allign with NPM api.

    def __str__(self):
        parts = []
        if self.directory:
            parts.append(f"Directory: {self.directory}")
        if self.repository_type:
            parts.append(f"Repository Type: {self.repository_type}")
        parts.append(f"URL: {self.url}")
        return "\n".join(parts)

    def __repr__(self):
        return f"Repository(directory={repr(self.directory)}, repository_type={repr(self.repository_type)}, url={repr(self.url)})"


class Funding(BaseModel, NSPrettyPrintable):
    # Nick added dict[str, str] and None to allign with npm api
    funding_type: str | dict[str, str] | None = Field(..., alias="type")
    # Nick added dict[str, str] to allign with npm api
    url: str | dict[str, str]

    def __str__(self):
        return f"Funding(type={self.funding_type}, url={self.url})"

    def __repr__(self):
        return f"Funding(funding_type={repr(self.funding_type)}, url={repr(self.url)})"


class Overrides(RootModel, NSPrettyPrintable):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # This needs recursion, hence using a forward reference
    root: dict[str, Union[str, "Overrides"]]

    @classmethod
    def recursive_repr(cls, obj):
        if isinstance(obj, Overrides):
            return f"Overrides({{{', '.join(f'{key}: {cls.recursive_repr(value)}' for key, value in obj.root.items())}}})"
        elif isinstance(obj, str):
            return f"'{obj}'"
        return repr(obj)

    def __str__(self):
        return Overrides.recursive_repr(self)

    def __repr__(self):
        return f"Overrides({Overrides.recursive_repr(self)})"


class PeerDependencyMeta(BaseModel, NSPrettyPrintable):
    optional: bool

    def __str__(self):
        return f"optional: {self.optional}"

    def __repr__(self):
        return f"PeerDependencyMeta(optional={self.optional})"


class DeprecatedLicense(BaseModel, NSPrettyPrintable):
    license_type: str = Field(..., alias="type")
    url: str

    def __str__(self):
        return f"license_type: {self.license_type}, url: {self.url}"

    def __repr__(self):
        return f"DeprecatedLicense(license_type={self.license_type}, url={self.url})"


# Signature (used in dist)
class Signature(BaseModel, NSPrettyPrintable):
    sig: str
    keyid: str

    def __str__(self):
        return f"sig: {self.sig}, keyid: {self.keyid}"

    def __repr__(self):
        return f"Signature(sig={self.sig}, keyid={self.keyid})"


# Dist (properties of Packument.versions)
class Dist(BaseModel, NSPrettyPrintable):
    # deprecated?  (ref: found in uuid@0.0.2)
    bin: dict[str, dict[str, str]] | None = (
        None  # A dictionary for `shasum` and `tarball`
    )

    # the number of files in the tarball. this is on most packages published >= 2018
    file_count: int | None = Field(None, alias="fileCount")

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
    unpacked_size: int | None = Field(None, alias="unpackedSize")

    def __str__(self):
        output = "Dist:\n"
        if self.bin is not None:
            output += f"\t{'bin':<20}: {self.bin}\n"
        if self.file_count is not None:
            output += f"\t{'file_count':<20}: {self.file_count}\n"
        if self.integrity is not None:
            output += f"\t{'integrity':<20}: {self.integrity}\n"
        if self.npm_signature is not None:
            output += f"\t{'npm_signature':<20}: {self.npm_signature}\n"
        output += f"\t{'shasum':<20}: {self.shasum}\n"
        if self.signatures:
            output += f"\t{'signatures':<20}: {[repr(sig) for sig in self.signatures]}\n"
        if self.tarball is not None:
            output += f"\t{'tarball':<20}: {self.tarball}\n"
        if self.unpacked_size is not None:
            output += f"\t{'unpacked_size':<20}: {self.unpacked_size}\n"
        return output

    def __repr__(self):
        # This will return a more technical representation for debugging
        return (
            f"Dist(bin={self.bin}, file_count={self.file_count}, "
            f"integrity={self.integrity}, npm_signature={self.npm_signature}, "
            f"shasum={self.shasum}, signatures={self.signatures}, "
            f"tarball={self.tarball}, unpacked_size={self.unpacked_size})"
        )


# DevEngineDependency (used in DevEngines)
class DevEngineDependency(BaseModel, NSPrettyPrintable):
    name: str
    version: str | None = None
    on_fail: (
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True,
                pattern=r"^(ignore|warn|error|download)$",  # Regex pattern constraint
            ),
        ]
        | None
    ) = Field("warn", alias="onFail")

    def __str__(self):
        output = f"DevEngineDependency(name: {self.name}"
        if self.version:
            output += f", version: {self.version}"
        output += f", on_fail: {self.on_fail})"
        return output

    def __repr__(self):
        return f"DevEngineDependency(name={repr(self.name)}, version={repr(self.version)}, on_fail={repr(self.on_fail)})"


class DevEngines(BaseModel, NSPrettyPrintable):
    os: DevEngineDependency | list[DevEngineDependency] | None = None
    cpu: DevEngineDependency | list[DevEngineDependency] | None = None
    libc: DevEngineDependency | list[DevEngineDependency] | None = None
    runtime: DevEngineDependency | list[DevEngineDependency] | None = None
    package_manager: DevEngineDependency | list[DevEngineDependency] | None = Field(
        None, alias="packageManager"
    )

    def __str__(self):
        def _format_field(field_name: str, field_value):
            if field_value is None:
                return ""
            if isinstance(field_value, list):
                return f"\t{field_name}:\n" + "".join(
                    [f"\t  - {item}\n" for item in field_value]
                )
            return f"\t{field_name}: {field_value}\n"

        output = "DevEngines:\n"
        for field_name in ["os", "cpu", "libc", "runtime", "package_manager"]:
            field_value = getattr(self, field_name)
            field_str = _format_field(field_name, field_value)
            output += field_str
        return output.strip()

    def __repr__(self):
        return (
            f"DevEngines(os={repr(self.os)}, cpu={repr(self.cpu)}, libc={repr(self.libc)}, "
            f"runtime={repr(self.runtime)}, package_manager={repr(self.package_manager)})"
        )


class Bugs(TypedDict):
    email: str | None
    url: str | None

    #
    #     if isinstance(values.get("url"), str):
    #         values["url"] = values["url"]  # You could populate email here if necessary
    #     if isinstance(values.get("url"), str):
    #         values["url"] = values["url"]  # You could populate email here if necessary
    #     return values
    #
    # def __str__(self):
    #     output = "Bugs Information:\n"
    #     if self.email:
    #         output += f"\tEmail: {self.email}\n"
    #     if self.url:
    #         output += f"\tURL: {self.url}\n"
    #     return output.strip()
    #
    # def __repr__(self):
    #     return f"Bugs(email={repr(self.email)}, url={repr(self.url)})"
    #


class Contact(BaseModel, NSPrettyPrintable):
    name: str
    email: str | None = None
    url: str | None = None

    def __str__(self):
        output = "Contact Information:\n"
        output += f"\tName: {self.name}\n"
        if self.email:
            output += f"\tEmail: {self.email}\n"
        if self.url:
            output += f"\tURL: {self.url}\n"
        return output.strip()

    def __repr__(self):
        return f"Contact(name={repr(self.name)}, email={repr(self.email)}, url={repr(self.url)})"


class PackageJSON(BaseModel, NSPrettyPrintable):
    """
    This is in the tarball for the project. it really could have anything in it.
    """

    model_config = ConfigDict(extra="allow")  # Allow extra fields

    # Required Fields
    name: str
    version: str

    # Optional Fields
    author: Contact | str | None = None
    bin: dict[str, str] | None = None
    # Nick added bool to the dict to align with the NPM api
    browser: dict[str, str | bool] | str | None = None
    bugs: Bugs | str | None = None
    bundled_dependencies: list[str] | bool | None = Field(
        None, alias="bundledDependencies"
    )
    bundle_dependencies: list[str] | bool | None = Field(None, alias="bundleDependencies")
    config: dict[str, Any] | None = None
    contributors: list[Contact | str] | None = None
    cpu: list[str] | None = None
    dependencies: dict[str, str] | None = None
    description: str | None = None
    dev_dependencies: dict[str, str] | None = Field(None, alias="devDependencies")
    dev_engines: DevEngines | None = Field(None, alias="devEngines")
    directories: dict[str, str] | None = None
    engines: dict[str, str] | str | None = None  # Nick added string to align with NPM api
    files: list[str] | None = None
    # Nick changed this a lot to align with the npm api
    funding: dict[str, str] | list[Funding] | Funding | str | None = None
    homepage: str | None = None
    keywords: list[str] | None = None
    license: str | dict[str, str] | None = None
    licenses: DeprecatedLicense | list[DeprecatedLicense] | None = None
    main: str | None = None
    man: str | list[str] | None = None
    optional_dependencies: dict[str, str] | None = Field(
        None, alias="optionalDependencies"
    )
    os: list[str] | None = None
    overrides: Overrides | None = None
    peer_dependencies: dict[str, str] | None = Field(None, alias="peerDependencies")
    peer_dependencies_meta: dict[str, PeerDependencyMeta] | None = Field(
        None, alias="peerDependenciesMeta"
    )
    private: bool | None = None
    publish_config: dict[str, Any] | None = None
    repository: Repository | str | None = None
    scripts: dict[str, str] | None = None
    # https://www.typescriptlang.org/docs/handbook/declaration-files/dts-from-js.html#editing-the-packagejson
    types: str | None = None
    workspaces: list[str] | dict[str, str] | None = None

    # @model_validator(mode="before")
    # def detect_extra_fields(cls, values):
    #     # Extract the defined field names from the class
    #     defined_fields = set(cls.__annotations__.keys())
    #     input_fields = set(values.keys())
    #
    #     # Detect extra fields
    #     extra_fields = input_fields - defined_fields
    #
    #     if extra_fields:
    #         # Issue a warning for extra fields
    #         app.logger.warning(
    #             f"Extra fields detected: {', '.join(extra_fields)}",
    #             stacklevel=2,
    #         )
    #
    #     return values

    def __str__(self):
        output = "PackageJSON Information:\n"

        def format_field(name, value, width=20):
            return f"{name:<{width}}: {value}"

        # Required Fields
        output += f"{format_field('name', self.name)}\n"
        output += f"{format_field('version', self.version)}\n"

        # Optional Fields
        if self.author:
            output += f"{format_field('author', str(self.author))}\n"
        if self.bin:
            output += f"{format_field('bin', str(self.bin))}\n"
        if self.bugs:
            output += f"{format_field('bugs', str(self.bugs))}\n"
        if self.bundled_dependencies:
            output += f"{format_field('bundled_dependencies', str(self.bundled_dependencies))}\n"
        if self.bundle_dependencies:
            output += (
                f"{format_field('bundle_dependencies', str(self.bundle_dependencies))}\n"
            )
        if self.config:
            output += f"{format_field('config', str(self.config))}\n"
        if self.contributors:
            output += f"{format_field('contributors', str(self.contributors))}\n"
        if self.cpu:
            output += f"{format_field('cpu', str(self.cpu))}\n"
        if self.dependencies:
            output += f"{format_field('dependencies', str(self.dependencies))}\n"
        if self.description:
            output += f"{format_field('description', str(self.description))}\n"
        if self.dev_dependencies:
            output += f"{format_field('dev_dependencies', str(self.dev_dependencies))}\n"
        if self.dev_engines:
            output += f"{format_field('dev_engines', str(self.dev_engines))}\n"
        if self.directories:
            output += f"{format_field('directories', str(self.directories))}\n"
        if self.engines:
            output += f"{format_field('engines', str(self.engines))}\n"
        if self.files:
            output += f"{format_field('files', str(self.files))}\n"
        if self.funding:
            output += f"{format_field('funding', str(self.funding))}\n"
        if self.homepage:
            output += f"{format_field('homepage', self.homepage)}\n"
        if self.keywords:
            output += f"{format_field('keywords', str(self.keywords))}\n"
        if self.license:
            output += f"{format_field('license', self.license)}\n"
        if self.licenses:
            output += f"{format_field('licenses', str(self.licenses))}\n"
        if self.main:
            output += f"{format_field('main', self.main)}\n"
        if self.man:
            output += f"{format_field('man', str(self.man))}\n"
        if self.optional_dependencies:
            output += f"{format_field('optional_dependencies', str(self.optional_dependencies))}\n"
        if self.os:
            output += f"{format_field('os', str(self.os))}\n"
        if self.overrides:
            output += f"{format_field('overrides', str(self.overrides))}\n"
        if self.peer_dependencies:
            output += (
                f"{format_field('peer_dependencies', str(self.peer_dependencies))}\n"
            )
        if self.peer_dependencies_meta:
            output += f"{format_field('peer_dependencies_meta', str(self.peer_dependencies_meta))}\n"
        if self.private:
            output += f"{format_field('private', str(self.private))}\n"
        if self.publish_config:
            output += f"{format_field('publish_config', str(self.publish_config))}\n"
        if self.repository:
            output += f"{format_field('repository', str(self.repository))}\n"
        if self.scripts:
            output += f"{format_field('scripts', str(self.scripts))}\n"
        if self.types:
            output += f"{format_field('types', self.types)}\n"
        if self.workspaces:
            output += f"{format_field('workspaces', str(self.workspaces))}\n"

        return output.strip()

    def __repr__(self):
        return (
            f"PackageJSON(name={repr(self.name)}, version={repr(self.version)}, "
            f"author={repr(self.author)}, bin={repr(self.bin)}, bugs={repr(self.bugs)}, "
            f"bundled_dependencies={repr(self.bundled_dependencies)}, "
            f"bundle_dependencies={repr(self.bundle_dependencies)}, "
            f"config={repr(self.config)}, contributors={repr(self.contributors)}, "
            f"cpu={repr(self.cpu)}, dependencies={repr(self.dependencies)}, "
            f"description={repr(self.description)}, "
            f"dev_dependencies={repr(self.dev_dependencies)}, "
            f"dev_engines={repr(self.dev_engines)}, directories={repr(self.directories)}, "
            f"engines={repr(self.engines)}, files={repr(self.files)}, "
            f"funding={repr(self.funding)}, homepage={repr(self.homepage)}, "
            f"keywords={repr(self.keywords)}, license={repr(self.license)}, "
            f"licenses={repr(self.licenses)}, main={repr(self.main)}, "
            f"man={repr(self.man)}, optional_dependencies={repr(self.optional_dependencies)}, "
            f"os={repr(self.os)}, overrides={repr(self.overrides)}, "
            f"peer_dependencies={repr(self.peer_dependencies)}, "
            f"peer_dependencies_meta={repr(self.peer_dependencies_meta)}, "
            f"private={repr(self.private)}, publish_config={repr(self.publish_config)}, "
            f"repository={repr(self.repository)}, scripts={repr(self.scripts)}, "
            f"types={repr(self.types)}, workspaces={repr(self.workspaces)})"
        )


def get_non_null_attributes(obj):
    return {key: value for key, value in vars(obj).items() if value is not None}


# def get_descriminator_value(v: Any) -> str:
#     if isinstance(v, dict):
#         return v.get("url", v.get("email"))
#     return getattr(v, "url", getattr(v, "email", None))
#


class PackumentVersion(PackageJSON, NSPrettyPrintable):
    """
    Note: Contacts (bugs, author, contributors, repository, etc) can be simple
    strings in package.json, but not in registry metadata.
    """

    id: str = Field(..., alias="_id")
    # This is supposed to be required according to interfaces.d.ts of npm @types. But
    # packages like @amory/transform-react-pug don't have it. So I made it optional
    npm_version: str | None = Field(None, alias="_npmVersion")
    dist: Dist

    has_shrinkwrap: bool | None = Field(None, alias="_hasShrinkwrap")
    # optional (ref: not defined in uuid@1.4.0)
    node_version: str | None = Field(None, alias="_nodeVersion")
    npm_user: Contact | None = Field(None, alias="_npmUser")
    git_head: str | None = Field(None, alias="gitHead")
    author: Contact | None = None  # type: ignore[reportIncompatibleVariableOverride]
    bugs: Bugs | None = None  # type: ignore[reportIncompatibleVariableOverride]

    # bugs: Annotated[
    #     Union[
    #         Annotated[Bugs, Tag("bugs")],
    #         Annotated[str, Tag("string")],
    #     ],
    #     Discriminator(get_descriminator_value),
    # ]
    contributors: list[Contact] | None = None  # type: ignore[reportIncompatibleVariableOverride]
    maintainers: list[Contact] | None = None
    readme: str | None = None
    readme_filename: str | None = Field(None, alias="readmeFilename")
    repository: Repository | None = None  # type: ignore[reportIncompatibleVariableOverride]
    deprecated: str | bool | None = None  # I added bool to the options.

    def __str__(self):
        def format_field(name, value, width=20):
            return f"{name:<{width}}: {value}"

        output = "PackumentVersion Information:\n"

        # Required Fields
        output += f"{format_field('id', self.id)}\n"
        output += f"{format_field('dist', str(self.dist))}\n"

        # Optional Fields
        if self.npm_version:
            output += f"{format_field('npm_version', str(self.npm_version))}\n"
        if self.has_shrinkwrap:
            output += f"{format_field('has_shrinkwrap', str(self.has_shrinkwrap))}\n"
        if self.node_version:
            output += f"{format_field('node_version', self.node_version)}\n"
        if self.npm_user:
            output += f"{format_field('npm_user', str(self.npm_user))}\n"
        if self.git_head:
            output += f"{format_field('git_head', self.git_head)}\n"
        if self.author:
            output += f"{format_field('author', str(self.author))}\n"
        elif super().author:
            output += f"{format_field('author', str(super().author))}\n"
        if self.bugs:
            output += f"{format_field('bugs', str(self.bugs))}\n"
        elif super().bugs:
            output += f"{format_field('bugs', str(super().bugs))}\n"
        if self.contributors:
            output += f"{format_field('contributors', str(self.contributors))}\n"
        elif super().contributors:
            output += f"{format_field('contributors', str(super().contributors))}\n"
        if self.repository:
            output += f"{format_field('repository', str(self.repository))}\n"
        elif super().repository:
            output += f"{format_field('repository', str(super().repository))}\n"
        if self.maintainers:
            output += f"{format_field('maintainers', str(self.maintainers))}\n"
        if self.readme:
            output += f"{format_field('readme', self.readme[:100] + '...')}\n"  # Truncate readme to first 100 chars
        if self.readme_filename:
            output += f"{format_field('readme_filename', self.readme_filename)}\n"
        if self.deprecated:
            output += f"{format_field('deprecated', self.deprecated)}\n"

        # Include fields from PackageJSON (super class)
        output += super().__str__()

        return output.strip()

    def __repr__(self):
        return (
            f"PackumentVersion(id={repr(self.id)}, npm_version={repr(self.npm_version)}, "
            f"dist={repr(self.dist)}, has_shrinkwrap={repr(self.has_shrinkwrap)}, "
            f"node_version={repr(self.node_version)}, npm_user={repr(self.npm_user)}, "
            # f"git_head={repr(self.git_head)}, author={repr(self.author) if self.author else repr(super().author)}, "
            f"bugs={repr(self.bugs) if self.bugs else repr(super().bugs)}, "
            f"maintainers={repr(self.maintainers)}, readme={repr(self.readme)}, "
            # f"readme_filename={repr(self.readme_filename)}, repository={repr(self.repository) if self.repository else repr(super().repository)}, "
            f"deprecated={repr(self.deprecated)}, "
            f"{super().__repr__()[1:]} )"  # Append parent class fields after the opening parenthesis
        )


# Packument (root model for npm metadata)
class Packument(BaseModel, NSPrettyPrintable):
    """
    This is what you get from the npm api.
    """

    id: str = Field(..., alias="_id")
    rev: str | None = Field(
        None, alias="_rev"
    )  # Nick added None to align with the npm api
    time: dict[str, str]  # modified and created can be required, other fields allowed
    versions: dict[str, PackumentVersion]

    cached: bool | None = Field(None, alias="_cached")
    dist_tags: dict[str, str | None] = Field(
        ..., alias="dist-tags"
    )  # dist-tags can include 'latest'
    # Users are represented as a dict with string keys and `True` values
    users: dict[str, bool] | None = None

    # Hoisted fields from latest PackumentVersion
    name: str
    git_head: str | None = Field(None, alias="gitHead")
    author: Contact | None = None  # type: ignore[reportIncompatibleVariableOverride]
    bugs: Bugs | None = None  # type: ignore[reportIncompatibleVariableOverride]
    contributors: list[Contact] | None = None  # type: ignore[reportIncompatibleVariableOverride]
    maintainers: list[Contact] | None = None
    readme: str | None = None
    readme_filename: str | None = Field(None, alias="readmeFilename")
    repository: Repository | None = None  # type: ignore[reportIncompatibleVariableOverride]
    description: str | None = None
    homepage: str | None = None
    keywords: list[str] | None = None
    license: str | None = None

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> "Packument | None":
        try:
            return cls.model_validate(json_data)  # Validate and create the model
        except ValidationError as e:
            print(f"Validation error: {e}")
            return None

    def get_latest_version(self) -> str | None:
        if not self.versions:
            return None
        if len(self.versions) == 1:
            return next(iter(self.versions.keys()))  # Get the first key

        dist_tags = self.dist_tags
        if dist_tags and dist_tags.get("latest"):
            return dist_tags.get("latest")

        from packaging import version

        return max(self.versions.keys(), key=version.parse)

    def get_dependencies(self, version_key: str) -> list[str]:
        version = self.versions[version_key]
        if version.dependencies is None:
            return []
        return list(version.dependencies.keys())


# ManifestVersion (same structure as PackumentVersion, but trimmed)
class ManifestVersion(PackumentVersion, NSPrettyPrintable):
    has_shrinkwrap: bool | None = Field(None, alias="_hasShrinkwrap")
    bin: dict[str, str] | None = None
    bundled_dependencies: list[str] | bool | None = Field(
        None, alias="bundledDependencies"
    )
    bundle_dependencies: list[str] | bool | None = Field(None, alias="bundleDependencies")
    dependencies: dict[str, str] | None = None
    deprecated: str | bool | None = None
    dev_dependencies: dict[str, str] | None = Field(None, alias="devDependencies")
    directories: dict[str, str] | None = None
    dist: Dist
    engines: dict[str, str] | None = None
    name: str
    optional_dependencies: dict[str, str] | None = Field(
        None, alias="optionalDependencies"
    )
    peer_dependencies: dict[str, str] | None = Field(None, alias="peerDependencies")
    version: str


class Manifest(BaseModel, NSPrettyPrintable):
    """
    abbreviated metadata format (aka corgi)

    https://github.com/npm/registry/blob/master/docs/responses/package-metadata.md#abbreviated-metadata-format
    returned from registry requests with accept header values containing
    `application/vnd.npm.install-v1+json`

    Manifest (root metadata with versions)
    """

    modified: str
    versions: dict[str, ManifestVersion]
    cached: bool | None = Field(None, alias="_cached")
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
