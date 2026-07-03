# Docker

## Was ist Docker?

Docker ist eine Plattform, die eine Anwendung zusammen mit allem, was sie zum Laufen braucht — Code, Laufzeit, Abhängigkeiten, Umgebungsvariablen und Konfiguration — in eine einzige Einheit namens **Container** verpackt.

Ein Container ist vom Hostsystem und von anderen Containern isoliert. Das löst das klassische "läuft bei mir"-Problem: Wenn es im Container läuft, läuft es überall, wo Docker installiert ist.

Grundlegende Konzepte:

| Begriff | Beschreibung |
|---|---|
| **Image** | Ein unveränderlicher Bauplan für einen Container (wie eine Klasse) |
| **Container** | Eine laufende Instanz eines Images (wie ein Objekt) |
| **Dockerfile** | Eine Textdatei mit Anweisungen zum Bauen eines Images |
| **Registry** | Ein Speicherdienst für Images (z.B. Docker Hub) |
| **Volume** | Eine Möglichkeit, Host-Verzeichnisse in einen Container einzubinden |

---

## Woher bekommt man Images?

### Docker Hub — [hub.docker.com](https://hub.docker.com)

Die Standard-Public-Registry. Images werden automatisch von dort gezogen, wenn `docker pull <name>` ausgeführt wird.

```bash
docker pull python:3.14-slim     # offizielles Python-Image
docker pull postgres:17          # offizielles PostgreSQL-Image
```

**Offizielle Images** (gepflegt von den Software-Herstellern) sind mit einem blauen Badge markiert. Diese gegenüber Community-Images für Basis-Images bevorzugen.

**Image-Tags** steuern die Version:
- `python:3.14-slim` — spezifische Version, minimales OS (empfohlen für Produktion)
- `python:latest` — immer die neueste Version (unvorhersehbar, in Produktion vermeiden)
- `python:3.14` — vollständiges Debian-Image, deutlich größer

### GitHub Container Registry — `ghcr.io`

Wird von Open-Source-Projekten verwendet, die ihre eigenen Images zusammen mit ihrem Code hosten.

```bash
# Beispiel: uv (der Python-Paketmanager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
```

### Andere Registries

| Registry | URL | Häufige Verwendung |
|---|---|---|
| AWS ECR | `<account>.dkr.ecr.<region>.amazonaws.com` | Private Images auf AWS |
| Google Artifact Registry | `<region>-docker.pkg.dev` | Private Images auf GCP |
| Azure Container Registry | `<name>.azurecr.io` | Private Images auf Azure |

Bei Produktions-ETL-Pipelines schieben Teams ihre eigenen Images typischerweise in eine private Registry, um Versionierung und Zugriff zu kontrollieren.

---

## Docker in ETL-Pipelines

Docker wird in ETL häufig verwendet, weil Pipelines strenge Umgebungsanforderungen haben (genaue Python-Version, spezifische Bibliotheksversionen, Abhängigkeiten auf OS-Ebene) und zuverlässig auf lokalen Rechnern, CI/CD-Systemen und Cloud-Schedulern laufen müssen.

### Muster 1: Containerisiertes Pipeline-Skript

Das einfachste Muster — die gesamte Pipeline als ein Image verpacken und nach einem Zeitplan ausführen.

```
Scheduler (cron / Airflow / Prefect)
    └── docker run customer-data-platform
            └── extract → validate → transform → load
```

Das macht dieses Projekt. Der Container führt `main.py` aus, beendet sich und stoppt.

```bash
docker run --rm -v ./data:/app/data customer-data-platform
```

### Muster 2: Ein Container pro Stage

Jede ETL-Stage läuft in ihrem eigenen Container. Nützlich, wenn Stages widersprüchliche Abhängigkeiten haben oder unabhängig skaliert werden müssen.

```
Extract-Container  →  (schreibt nach S3 / geteiltem Volume)
Transform-Container  →  (liest von S3, schreibt Ergebnis)
Load-Container  →  (liest Ergebnis, schreibt in DB)
```

Orchestratoren wie Apache Airflow oder Prefect verwalten die Abhängigkeiten zwischen den Stages mithilfe von `DockerOperator` oder ähnlichen Task-Typen.

### Muster 3: Container in Orchestrierungsplattformen

In größeren Setups laufen Container innerhalb von Kubernetes (K8s) oder einem verwalteten Dienst:

| Plattform | Beschreibung |
|---|---|
| **Kubernetes + CronJob** | Container auf einem Cluster einplanen |
| **AWS ECS / Fargate** | Container ohne Serververwaltung ausführen |
| **Google Cloud Run Jobs** | Serverlose Container-Ausführung |
| **Azure Container Instances** | Einfache On-Demand-Container-Ausführung |

Diese Plattformen übernehmen Skalierung, Wiederholungen und Logging — der Pipeline-Code bleibt unverändert, da er nur ein Container ist.

### Warum Docker gut zu ETL passt

- **Reproduzierbarkeit** — dasselbe Image läuft in Entwicklung, Staging und Produktion
- **Isolierung** — verschiedene Pipelines können verschiedene Python-Versionen verwenden, ohne Konflikte
- **Portabilität** — Cloud-Provider wechseln, ohne die Pipeline neu zu schreiben
- **Versionierung** — Images sind getaggt, Rollbacks sind eine einzeilige Änderung
- **Abhängigkeiten einfrieren** — `uv pip install .` zur Build-Zeit erfasst exakte Paketversionen im Image-Layer

---

## Häufige Befehle

```bash
# Image aus dem Dockerfile im aktuellen Verzeichnis bauen
docker build -t my-pipeline .

# Container ausführen (--rm entfernt ihn nach dem Beenden)
docker run --rm my-pipeline

# Lokales Verzeichnis in den Container einbinden
docker run --rm -v ./data:/app/data my-pipeline

# Umgebungsvariablen übergeben
docker run --rm -e DB_URL=sqlite:///app/db.sqlite my-pipeline

# Laufende Container auflisten
docker ps

# Alle Images auflisten
docker images

# Ein Image entfernen
docker rmi my-pipeline
```
