# DevHub AI - OAuth Provider Strategy Architecture

## Provider Strategy Design Pattern

To support future OAuth providers (Google, GitHub, Microsoft, Facebook, GitLab, LinkedIn) without modifying core authentication logic, the system utilizes the **Strategy Pattern**.

```
                           ┌──────────────────┐
                           │  IOAuthProvider  │ (Abstract Interface)
                           └────────┬─────────┘
                                    │
       ┌────────────────────┬───────┴────────────┬───────────────────┐
┌──────┴───────┐   ┌────────┴────────┐   ┌───────┴────────┐   ┌──────┴──────┐
│GoogleProvider│   │ GitHubProvider  │   │MSFTProvider    │   │... Provider │
└──────────────┘   └─────────────────┘   └────────────────┘   └─────────────┘
```

## Lifecycle & Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as End User
    participant App as Frontend Application
    participant Strategy as OAuthProviderStrategy
    participant Provider as OAuth Provider (e.g. Google/GitHub)
    participant AuthEngine as Auth Engine / DB

    User->>App: Clicks "Sign in with Google"
    App->>Strategy: Request Auth URL (provider="google")
    Strategy-->>App: Redirect URL + CSRF state token
    App->>Provider: Redirect User to Provider OAuth Page
    User->>Provider: Authorizes DevHub AI
    Provider-->>App: Callback to /auth/callback?code=123&state=xyz
    App->>Strategy: POST code & state
    Strategy->>Provider: Exchange code for access_token & id_token
    Provider-->>Strategy: Tokens & User Profile claims
    Strategy->>AuthEngine: Map/Link User profile (Account Linking)
    AuthEngine-->>App: Return DevHub JWT Token Pair
```
