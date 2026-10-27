# OpenShell sandbox run, demonstrated 2026-10-27

Why a sandbox here: the medico-legal poisoning register is sensitive. The surveillance brief reads the whole register,
so it runs in an NVIDIA OpenShell sandbox that can reach exactly one service, the Nebius Token Factory model endpoint.
Not Tavily, not the open web. The real API key never enters the sandbox.

Environment: Windows 11, WSL2 Ubuntu 24.04, Docker Desktop 29.5.3, OpenShell 0.1.4 (same gateway setup as Sieve; see
`sieve/infra/openshell/DEMONSTRATED.md`). Command: `bash infra/openshell/run.sh` with `NEBIUS_API_KEY` exported.

## Observed

Before any provider is attached (deny by default):

```
https://api.tavily.com -> blocked: ConnectError
https://example.com -> blocked: ConnectError
https://api.tokenfactory.nebius.com/v1/models -> blocked: ConnectError
```

After attaching only the Token Factory provider:

```
https://api.tavily.com -> blocked: ConnectError
https://example.com -> blocked: ConnectError
https://api.tokenfactory.nebius.com/v1/models -> 401        (reachable; this probe sends no key)
NEBIUS_API_KEY=opensh... (placeholder)
```

The surveillance brief, run inside the sandbox:

```
INSIDE OPENSHELL SANDBOX: alerts ['spraying cluster', 'banned chemical in circulation', 'restricted-use chemicals'] | case reports read 32 | tokens 229294
headline: Organophosphate spraying cluster and banned chemicals in circulation drive acute poisonings in the district
  trace Nemotron 3.5 Lightning surveillance.brief 194150 $0.0119
```

So the only place register data went was Nemotron 3.5 Lightning on Token Factory, with a key the process never held.

## Lessons

- Run the virtual environment's interpreter (`/workspace/.venv/bin/python`). Its resolved binary is
  `/usr/local/bin/python3.12`, which is what the policy matches; running the system interpreter directly loses the
  installed packages.
- A `.env` written on Windows has CRLF line endings; strip them before sourcing in WSL or every key gains a trailing
  carriage return.
- The gateway needs more than five seconds to accept connections on first start; poll `openshell status`.
