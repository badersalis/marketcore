#!/usr/bin/env python3
"""
Promote an existing user to the operator role.

Intended for bootstrapping the first operator on a fresh environment —
there is no API path to create the first operator (chicken-and-egg).

Usage:
    python auth-service/scripts/bootstrap_operator.py <email>

Environment:
    DATABASE_URL  PostgreSQL DSN for market_auth_db.
                  Defaults to the local-dev value.
                  asyncpg-style prefix (postgresql+asyncpg://) is accepted.

Examples:
    python auth-service/scripts/bootstrap_operator.py admin@example.com
    DATABASE_URL=postgresql://postgres:postgres@localhost:5432/market_auth_db \
        python auth-service/scripts/bootstrap_operator.py admin@example.com
"""

import argparse
import asyncio
import os
import sys

import asyncpg


_DEFAULT_DB = "postgresql://postgres:postgres@localhost:5432/market_auth_db"


def _normalize_url(url: str) -> str:
    # asyncpg does not accept the SQLAlchemy +asyncpg dialect prefix
    return url.replace("postgresql+asyncpg://", "postgresql://")


async def bootstrap(email: str) -> None:
    url = _normalize_url(os.getenv("DATABASE_URL", _DEFAULT_DB))

    try:
        conn = await asyncpg.connect(url)
    except Exception as exc:
        print(f"[error] Could not connect to database: {exc}")
        sys.exit(1)

    try:
        row = await conn.fetchrow(
            "SELECT id, email, role FROM users WHERE email = $1", email
        )

        if row is None:
            print(f"[error] No user found with email '{email}'.")
            print("        Register the account first, then run this script.")
            sys.exit(1)

        if row["role"] == "operator":
            print(f"[info]  {email} is already an operator — nothing to do.")
            return

        await conn.execute(
            "UPDATE users SET role = 'operator' WHERE email = $1", email
        )
        print(f"[ok]    {email}  (id={row['id']})  promoted to operator.")
        print("        Have the user log in again to receive an updated token.")

    finally:
        await conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Promote a registered user to the operator role."
    )
    parser.add_argument("email", help="Email address of the user to promote")
    args = parser.parse_args()

    asyncio.run(bootstrap(args.email))


if __name__ == "__main__":
    main()
