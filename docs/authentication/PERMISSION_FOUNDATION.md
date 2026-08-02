# DevHub AI - Role & Permission Foundation Architecture

## Overview

While full Role-Based Access Control (RBAC) is implemented in later workspace phases, this document establishes the foundational permission models, role hierarchies, and authorization boundaries.

---

## Role Hierarchy & Authorization Boundaries

```
┌─────────────────────────────────────────────────────────┐
│                      ADMIN ROLE                         │
│  (System-wide tenant administration, user management)   │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│                    MODERATOR ROLE                       │
│      (Workspace moderation, content policy audit)       │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│                      USER ROLE                          │
│     (Standard workspace member, personal content owner) │
└─────────────────────────────────────────────────────────┘
```

## Entity Ownership & Boundaries
- **User Entity**: Principal identity carrying roles (`admin`, `user`).
- **Workspace Ownership**: Workspaces maintain owner, editor, and viewer permission scopes.
- **Resource Boundary**: API authorization middleware verifies `user_id` matches resource ownership before granting access.
