# Antidote

Photograph a pesticide bottle. Antidote reads the label, names the chemical and its WHO hazard class, retrieves the cited guidance from the national poison-management module, or stops when there is no antidote, and fills the medico-legal register row.

Built for the Nebius x NVIDIA Global AI Hackathon on Nebius Token Factory with NVIDIA Nemotron 3 Nano, Super and Ultra. Apache-2.0.

Decision support for trained clinicians. Airway, breathing, circulation first. National Poisons Information Centre, AIIMS: 1800-116-117.

Status: scaffold. See `docs/IDEA.md`, `docs/PLAN.md`, `docs/TECHNICAL-DESIGN.md`, `docs/UX-DESIGN.md`.

## Quick start

```
cp .env.example .env   # add NEBIUS_API_KEY and TAVILY_API_KEY
make setup
make test
```
