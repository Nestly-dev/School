# Architecture Overview

```mermaid
flowchart TD
A[Mobile App] -->|JWT| B[API Gateway (Django+DRF)]
B --> C[Users app]
B --> D[Locations app (async)]
B --> E[Rides app]
B --> F[Cache Layer (LocMem/Redis)]
D -->|aiohttp| G[External Maps/Geocode]
B --> H[DB - SQLite/Postgres]

classDef svc fill:#eef,stroke:#88f,stroke-width:1px
class C,D,E,F,H svc