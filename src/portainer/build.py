from typing import Dict, Any
from pathlib import Path
import requests  # type: ignore
import docker  # type: ignore


def portainer_login(username: str, password: str) -> Dict[str, Any]:
    """Logs into portainer and returns a session and the portainer version"""
    auth_login = {"username": username, "password": password}
    auth_response = requests.post("http://127.0.0.1:9000/api/auth", json=auth_login)
    auth_response.raise_for_status()
    auth_token = auth_response.json()["jwt"]
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {auth_token}"})
    portainer_response = session.get("http://127.0.0.1:9000/api/system/version")
    portainer_response.raise_for_status()
    portainer_version = portainer_response.json()["ServerVersion"]
    return {"session": session, "version": portainer_version, "auth_token": auth_token}


def fetch_portainer_api_spec(version: str): # -> Dict[str, Any]:
    """Gets and caches the portainer api spec for a given version"""
    if not Path(f".cache/portainer_api/{version}/swagger.json").exists():
        Path(f".cache/portainer_api/{version}").mkdir(parents=True, exist_ok=True)
        json_request = requests.get(f"https://api.swaggerhub.com/apis/portainer/portainer-ce/{version}/swagger.json")
        json_request.raise_for_status()
        with open(f".cache/portainer_api/{version}/swagger.json", "w") as f:
            f.write(json_request.text)
    # with open(f".cache/portainer_api/{version}/swagger.json") as f:
    #     return f.read()


# def init_portainer_api(version: str, auth_token: str): # -> openapi.Swagger:
#     """
#         Returns a swagger api for portainer which follows the schema outlined here:
#         https://app.swaggerhub.com/apis/portainer/portainer-ce/2.19.4
#     """
#     # spec = get_portainer_api_spec(version)
#     # api = openapi.loads(spec)
#     # api.validate()
#     # return api
#     app = App.create(f"https://api.swaggerhub.com/apis/portainer/portainer-ce/{version}/swagger.json")
#     auth = Security(app)
#     auth.update_with("ApiKeyAuth", auth_token)
#     client = Client(auth)
#     return app, client

# def create_portainer_api(version: str, auth_token: str):
#     spec = get_portainer_api_spec(version)
#     api = openapi.loads(spec)
#     api.validate()
#     return api

def build_portainer_api(version: str):
    """Builds the portainer api"""
    # Path("src/portainer_api").mkdir(parents=True, exist_ok=True)
    docker_client = docker.from_env()
    docker_client.containers.run(
        "swaggerapi/swagger-codegen-cli",
        "generate -i /schemas/swagger.json -l python -o /local -D packageName=portainer",
        mounts = [
            docker.types.Mount(
                target="/local",
                source=str(Path().resolve()),
                type="bind"
            ),
            docker.types.Mount(
                target="/schemas",
                source=str(Path(f".cache/portainer_api/{version}").resolve()),
                type="bind"
            ),
        ],
        auto_remove=True,
    )


def init_portainer_api(username: str, password: str):
    portainer_session = portainer_login(username, password)
    fetch_portainer_api_spec(portainer_session["version"])
    build_portainer_api(portainer_session["version"])
    
def build():
    init_portainer_api("admin", "%a7DtJkb&^fG%aZKGNvga5V&yBU$#UYBfGjU*pu!v2HS288&kwbR7Gpd@A5MjWr2")

if __name__ == "__main__":
    build()
    # import portainer  # noqa: F401