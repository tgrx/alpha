# from configparser import ConfigParser
# from pathlib import Path
# from typing import Any
#
# import tomlkit
# from defusedxml.ElementTree import parse as parse_xml
# from dockerfile_parse import DockerfileParser
# from dotenv import dotenv_values
#
# from alpha.management.commands.rebranding_util import resolve_file
# from alpha.util import yaml
#
#
# def check_ci_deploy_dockerhub(
#     target: Path,
#     *,
#     dockerhub_image: str,
#     github_username: str,
# ) -> None:
#     target = resolve_file(target)
#     with target.open("r") as stream:
#         dom = yaml.load(stream)
#
#         job = dom["jobs"]["docker"]
#         assert job["if"] == f"github.actor == '{github_username}'"
#
#         step = next(
#             step
#             for step in job["steps"]
#             if step.get("id") == "deploy-to-dockerhub"
#         )
#
#         tags = step["with"]["tags"].split("\n")
#         tags_expected = [
#             f"{dockerhub_image}:${{{{ steps.build-args.outputs.version }}}}",
#             f"{dockerhub_image}:latest",
#             "",
#         ]
#
#         assert tags == tags_expected
#
#
# def check_ci_deploy_heroku(
#     target: Path,
#     *,
#     github_username: str,
#     heroku_app_maintainer_email: str,
#     heroku_app_name: str,
# ) -> None:
#     target = resolve_file(target)
#     with target.open("r") as stream:
#         dom = yaml.load(stream)
#
#         job = dom["jobs"]["heroku"]
#         assert job["if"] == f"github.actor == '{github_username}'"
#
#         step = next(
#             step
#             for step in job["steps"]
#             if step.get("id") == "deploy-to-heroku"
#         )
#         assert step["with"]["heroku_app_name"] == heroku_app_name
#         assert step["with"]["heroku_email"] == heroku_app_maintainer_email
#
#
# def check_codeowners(
#     target: Path,
#     *,
#     github_username: str,
# ) -> None:
#     target = resolve_file(target)
#     with target.open("r") as stream:
#         content = stream.read()
#         assert f"*   @{github_username}" in content
#
#
# def check_coveragerc(
#     target: Path,
#     *,
#     brand: str,
# ) -> None:
#     target = resolve_file(target)
#     rc = ConfigParser()
#     rc.read(target)
#     assert rc["html"]["title"] == brand
#
#
# def check_docker_compose(
#     target: Path,
#     *,
#     brand: str,
#     dockerhub_image: str,
# ) -> None:
#     psql_url = f"postgresql://e7a36973:a4f7a8c8@{brand}-db:5432/8fbbc147"
#     psql_volume = f"{brand}-db:/var/lib/postgresql/data"
#     test_service_url = f"http://{brand}-web"
#     web_service_image = f"{dockerhub_image}:dev"
#
#     target = resolve_file(target)
#     with target.open("r") as stream:
#         dom = yaml.load(stream)
#
#         services = dom["services"]
#
#         web = services.get(f"{brand}-web")
#         assert web is not None
#         assert web["container_name"] == f"{brand}-web"
#         assert f"{brand}-db" in web["depends_on"]
#         assert web["environment"]["DATABASE_URL"] == psql_url
#         assert web["image"] == web_service_image
#
#         db = services.get(f"{brand}-db")
#         assert db is not None
#         assert db["container_name"] == f"{brand}-db"
#         assert psql_volume in db["volumes"]
#
#         dba = services.get(f"{brand}-dba")
#         assert dba is not None
#         assert dba["container_name"] == f"{brand}-dba"
#         assert psql_volume in dba["volumes"]
#
#         qa = services.get(f"{brand}-qa")
#         assert qa is not None
#         assert qa["container_name"] == f"{brand}-qa"
#         assert f"{brand}-web" in qa["depends_on"]
#         assert qa["environment"]["DATABASE_URL"] == psql_url
#         assert qa["environment"]["TEST_SERVICE_URL"] == test_service_url
#         assert qa["image"] == web_service_image
#
#         volumes = dom["volumes"]
#
#         db = volumes.get(f"{brand}-db")
#         assert db is not None
#         assert db["name"] == f"{brand}-db"
#
#
# def check_dockerfile(
#     target: Path,
#     *,
#     description: str,
#     maintainer: str,
# ) -> None:
#     target = resolve_file(target)
#
#     dockerfile = DockerfileParser(target.as_posix())
#     labels = dockerfile.labels
#     assert labels["description"] == description
#     assert labels["org.opencontainers.image.authors"] == maintainer
#
#
# def check_dotenv(
#     target: Path,
#     *,
#     heroku_app_name: str,
# ) -> None:
#     target = resolve_file(target)
#     env = dotenv_values(target)
#     assert env["HEROKU_APP_NAME"] == heroku_app_name
#
#
# def check_pyproject_toml(
#     dirs: Any,
#     *,
#     maintainer: str,
#     description: str,
#     brand: str,
# ) -> None:
#     target = resolve_file(dirs.DIR_REPO / "pyproject.toml")
#     with target.open("r") as stream:
#         dom: Any = tomlkit.load(stream)
#         poetry = dom["tool"]["poetry"]
#         assert maintainer in poetry["authors"]
#         assert poetry["description"] == description
#         assert poetry["name"] == brand
#
#
# def check_readme_md(
#     dirs: Any,
#     *,
#     brand: str,
#     description: str,
# ) -> None:
#     target = resolve_file(dirs.DIR_REPO / "README.md")
#     with target.open("r") as stream:
#         content = stream.read()
#         assert f"# {brand.upper()}" in content
#         assert description in content
#
#
# def check_run_config(
#     target: Path,
#     *,
#     brand: str,
# ) -> None:
#     target = resolve_file(target)
#     with target.open("r") as stream:
#         tree = parse_xml(
#             stream,
#             forbid_dtd=True,
#             forbid_entities=True,
#             forbid_external=True,
#         )
#
#         node = tree.find("./configuration/module[1]")
#         assert node is not None
#         assert node.attrib["name"] == brand
