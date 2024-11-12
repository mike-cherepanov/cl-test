# cloud-linux-test

This is a test assignment for the CloudLinux Senior Python/Full Stack Developer role.

## QuickStart

This project uses Python3.12 and the [uv tool](https://docs.astral.sh/uv/) to manage dependencies. To install all dependencies, run the following command at the root of the project:

```bash
uv sync
source ./.venv/bin/activate
```

To ensure code quality, this project uses:

- [ruff](https://docs.astral.sh/ruff/) as linter and formatter
- [mypy](https://mypy.readthedocs.io/en/stable/) as static type checker
- [pytest](https://docs.pytest.org/en/stable/) as testing testing framework

To run all checks and automatic fix the following command should be run at the root of the project:

```bash
make fix
make check
```

To setup all environment like DB, Celery and Message Queue install [Docker Desktop](https://www.docker.com/products/docker-desktop) or [OrbStack](https://orbstack.dev)
and run command at the root of the porject:

```bash
docker-compose up -d
```

Web app will be available on http://127.0.0.1:8000/
