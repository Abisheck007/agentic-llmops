python -m pytest backend/tests/test_quality_checks.py -v

python -m pytest backend/tests/test_agent.py -v''

python -m pytest backend/tests -v

Remove-Item -Recurse -Force .git


docker --version
Docker version 29.8.2, build 7fc2dff
(.venv) PS C:\Users\balam\Music\suganya mam\classes\LLmops and agentops\agentic-rag-platform> docker compose version
Docker Compose version v5.5.1
(.venv) PS C:\Users\balam\Music\suganya mam\classes\LLmops and agentops\agentic-rag-platform> docker compose build
[+] Building 51.9s (21/21) FINISHED                                                                                                       
 => [internal] load local bake definitions                                                                                           0.0s
 => => reading from stdin 1.25kB                                                                                                     0.0s
 => [backend internal] load build definition from Dockerfile                                                                         0.1s
 => => transferring dockerfile: 445B                                                                                                 0.0s
 => [frontend internal] load build definition from Dockerfile                                                                        0.1s
 => => transferring dockerfile: 448B                                                                                                 0.0s
 => [backend internal] load metadata for docker.io/library/python:3.10-slim                                                          2.8s
 => [auth] library/python:pull token for registry-1.docker.io                                                                        0.0s
 => [backend internal] load .dockerignore                                                                                            0.0s
 => => transferring context: 207B                                                                                                    0.0s
 => [backend 1/6] FROM docker.io/library/python:3.10-slim@sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d    4.6s
 => => resolve docker.io/library/python:3.10-slim@sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d            0.0s
 => => sha256:cc1cbe171e30bea48715fd96ecf842ad9fae425ce5a18917bee871684eb836f1 249B / 249B                                           0.3s
 => => sha256:79f4247a2db52342f23c9ff6911633949443ca83b454d185a05ed6fc8689ffca 13.92MB / 13.92MB                                     1.1s
 => => sha256:1189ef607cc64ff2e2a214c12e5f46402dc316a1a62cc5adb7071616882df7ee 1.29MB / 1.29MB                                       1.0s
 => => sha256:ecc510c1e359bdc007b39802570bb7e4dec7d6ebccf357c3201a74299113e05e 29.84MB / 29.84MB                                     2.4s
 => => extracting sha256:ecc510c1e359bdc007b39802570bb7e4dec7d6ebccf357c3201a74299113e05e                                            1.1s
 => => extracting sha256:1189ef607cc64ff2e2a214c12e5f46402dc316a1a62cc5adb7071616882df7ee                                            0.2s
 => => extracting sha256:79f4247a2db52342f23c9ff6911633949443ca83b454d185a05ed6fc8689ffca                                            0.7s
 => => extracting sha256:cc1cbe171e30bea48715fd96ecf842ad9fae425ce5a18917bee871684eb836f1                                            0.0s
 => [backend internal] load build context                                                                                            0.2s
 => => transferring context: 92.83kB                                                                                                 0.1s
 => [frontend internal] load build context                                                                                           0.1s
 => => transferring context: 7.50kB                                                                                                  0.0s
 => [backend 2/6] WORKDIR /app                                                                                                       0.3s
 => [frontend 3/5] COPY frontend/requirements.txt /app/requirements.txt                                                              0.0s
 => [backend 3/6] COPY backend/requirements.txt /app/backend/requirements.txt                                                        0.1s
 => [frontend 4/5] RUN python -m pip install --no-cache-dir     -r /app/requirements.txt                                            24.9s
 => [backend 4/6] RUN python -m pip install --no-cache-dir     -r /app/backend/requirements.txt                                     32.2s
 => [frontend 5/5] COPY frontend/app.py /app/app.py                                                                                  0.1s
 => [frontend] exporting to image                                                                                                   18.4s
 => => exporting layers                                                                                                             14.3s
 => => exporting manifest sha256:3ba5375c4fe577600d2117c9b361a86797db3ddc6ab4b2f10e72a84c2f2a3aff                                    0.0s
 => => exporting config sha256:c93139bbdd92d18a8aae678740aa6cc2cdb342ef8915ce9a7d0e1d0cb3043946                                      0.0s
 => => exporting attestation manifest sha256:69c31ffceb327aa01e67118a7c694cb51a342742545a0507f6dc632b4240d074                        0.0s
 => => exporting manifest list sha256:fc6920a8d164ef9828a16cacd37b39e40ec76d272f12c4540ea789d1fcbc4099                               0.0s
 => => naming to docker.io/library/agentic-rag-platform-frontend:latest                                                              0.0s
 => => unpacking to docker.io/library/agentic-rag-platform-frontend:latest                                                           3.9s
 => [backend 5/6] COPY backend /app/backend                                                                                          0.1s
 => [backend 6/6] COPY data /app/data                                                                                                0.0s
 => [backend] exporting to image                                                                                                     9.9s
 => => exporting layers                                                                                                              4.6s
 => => exporting manifest sha256:8d70fbc08f26f6381e77a1337cd2862a269ddebd68217bcab3380e3a3d415efa                                    0.0s
 => => exporting config sha256:80b25d233cbe67f6591d0cd15eeedd58dc6de0f0c5dacf0e59c8eda5612f6afb                                      0.0s
 => => exporting attestation manifest sha256:c4ef61c180fc52b5b861c6fbac4ab7c8494c91d5ca1fa33347b350bfa7ad1557                        0.0s
 => => exporting manifest list sha256:c697e2acb83d8c7004045a65508021b3730e62254bf4701a3df4f0468caa457a                               0.0s
 => => naming to docker.io/library/agentic-rag-platform-backend:latest                                                               0.0s
 => => unpacking to docker.io/library/agentic-rag-platform-backend:latest                                                            5.1s
 => [backend] resolving provenance for metadata file                                                                                 0.0s
 => [frontend] resolving provenance for metadata file                                                                                0.0s
[+] build 2/2
 ✔ Image agentic-rag-platform-backend  Built                                                                                         52.1s
 ✔ Image agentic-rag-platform-frontend Built                                                                                         52.2s
(.venv) PS C:\Users\balam\Music\suganya mam\classes\LLmops and agentops\agentic-rag-platform> docker compose up -d
[+] up 2/3
 ✔ Network agentic-rag-platform_default      Created                                                                                  0.0s
 ✔ Container agentic-rag-platform-backend-1  Started                                                                                  0.4s
 - Container agentic-rag-platform-frontend-1 Starting                                                                                 0.4s
Error response from daemon: ports are not available: exposing port TCP 0.0.0.0:8501 -> 127.0.0.1:0: listen tcp 0.0.0.0:8501: bind: Only one usage of each socket address (protocol/network address/port) is normally permitted.

What's next:
    Debug this Compose error with Gordon → docker ai "help me fix this compose error"
(.venv) PS C:\Users\balam\Music\suganya mam\classes\LLmops and agentops\agentic-rag-platform> docker compose ps
NAME                             IMAGE                          COMMAND                  SERVICE   CREATED         STATUS         PORTS
agentic-rag-platform-backend-1   agentic-rag-platform-backend   "python -m uvicorn b…"   backend   6 seconds ago   Up 5 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
(.venv) PS C:\Users\balam\Music\suganya mam\classes\LLmops and agentops\agentic-rag-platform> docker compose logs --tail=100 backend
backend-1  | 2026-10-13 11:32:12,217 | INFO | backend.app.observability.tracing | Azure Monitor OpenTelemetry configured.
backend-1  | INFO:     Started server process [1]
backend-1  | INFO:     Waiting for application startup.
backend-1  | INFO:     Application startup complete.
backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
(.venv) PS C:\Users\balam\Music\suganya mam\classes\LLmops and agentops\agentic-rag-platform> docker compose logs --tail=100 frontend
(.venv) PS C:\Users\balam\Music\suganya mam\classes\LLmops and agentops\agentic-rag-platform> 


docker compose up -d --force-recreate backend

mapping


azure-openai-endpoint	AZURE_OPENAI_ENDPOINT
azure-openai-api-key	AZURE_OPENAI_API_KEY
azure-openai-deployment	AZURE_OPENAI_DEPLOYMENT
azure-openai-api-version	AZURE_OPENAI_API_VERSION
azure-ai-search-endpoint	AZURE_AI_SEARCH_ENDPOINT
azure-ai-search-index	AZURE_AI_SEARCH_INDEX
applicationinsights-connection-string	APPLICATIONINSIGHTS_CONNECTION_STRING


wsl --install
wsl --update