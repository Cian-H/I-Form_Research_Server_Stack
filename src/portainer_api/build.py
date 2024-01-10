from pathlib import Path
import requests  # type: ignore
import docker  # type: ignore


def fetch_portainer_api_spec(version: str):
    """Gets and caches the portainer api spec for a given version"""
    if not Path(f".cache/portainer_api/{version}/swagger.json").exists():
        Path(f".cache/portainer_api/{version}").mkdir(parents=True, exist_ok=True)
        json_request = requests.get(f"https://api.swaggerhub.com/apis/portainer/portainer-ce/{version}/swagger.json")
        json_request.raise_for_status()
        with open(f".cache/portainer_api/{version}/swagger.json", "w") as f:
            f.write(json_request.text)


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


def init_portainer_api():
    c = docker.from_env().containers.run("portainer/portainer-ce:latest", detach=True, tty=True, remove=True)
    portainer_version = c.exec_run("/portainer --version").output.decode().strip()
    c.stop()
    fetch_portainer_api_spec(portainer_version)
    build_portainer_api(portainer_version)
    
def build():
    init_portainer_api()

if __name__ == "__main__":
    build()