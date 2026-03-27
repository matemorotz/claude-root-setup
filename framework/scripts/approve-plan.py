#!/usr/bin/env python3
"""
Plan Approval Tool - Approve execution plans for dangerouslySkipPermissions

This tool allows you to approve execution plans, enabling them to use
dangerouslyDisableSandbox for Bash commands without prompting.

Usage:
    python approve-plan.py <plan_file.json>
    python approve-plan.py <plan_file.json> --expires 48h
    python approve-plan.py --list
    python approve-plan.py --revoke <plan_id>
    python approve-plan.py --enable-dangerous-skip

WARNING: Only approve plans you fully trust. Approved plans can execute
arbitrary Bash commands without sandboxing!
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional


class PlanApprovalManager:
    """Manages approved plans registry"""

    def __init__(self, registry_path: Path = None):
        if registry_path is None:
            registry_path = Path(__file__).parent.parent / "approved_plans.json"
        self.registry_path = registry_path
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        """Load approved plans registry"""
        if not self.registry_path.exists():
            return {
                "$schema": "approved-plans-schema",
                "version": "1.0.0",
                "approved_plans": {},
                "settings": {
                    "enable_dangerous_skip": False,
                    "require_explicit_approval": True,
                    "auto_expire_hours": 24
                },
                "audit_log": []
            }

        with open(self.registry_path) as f:
            return json.load(f)

    def _save_registry(self):
        """Save registry to disk"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def _compute_plan_hash(self, plan_content: str) -> str:
        """Compute SHA256 hash of plan content"""
        return hashlib.sha256(plan_content.encode()).hexdigest()[:16]

    def approve_plan(
        self,
        plan_path: Path,
        expires_hours: int = 24,
        note: str = ""
    ) -> Dict:
        """
        Approve a plan for dangerouslySkipPermissions

        Args:
            plan_path: Path to the plan JSON file
            expires_hours: Hours until approval expires
            note: Optional note about why this was approved

        Returns:
            Approval record
        """
        # Load and validate plan
        with open(plan_path) as f:
            plan_content = f.read()
            plan = json.loads(plan_content)

        if "plan_id" not in plan:
            raise ValueError("Plan missing 'plan_id' field")

        plan_id = plan["plan_id"]
        plan_hash = self._compute_plan_hash(plan_content)

        # Create approval record
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=expires_hours)

        approval = {
            "plan_id": plan_id,
            "plan_path": str(plan_path.absolute()),
            "plan_hash": plan_hash,
            "approved_at": now.isoformat() + "Z",
            "expires_at": expires_at.isoformat() + "Z",
            "expires_hours": expires_hours,
            "note": note,
            "status": "active"
        }

        # Add to registry
        self.registry["approved_plans"][plan_id] = approval

        # Add to audit log
        self.registry["audit_log"].append({
            "action": "approve",
            "plan_id": plan_id,
            "timestamp": now.isoformat() + "Z",
            "expires_hours": expires_hours,
            "note": note
        })

        self._save_registry()

        print(f"✅ Plan approved: {plan_id}")
        print(f"   Hash: {plan_hash}")
        print(f"   Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"   Duration: {expires_hours} hours")
        if note:
            print(f"   Note: {note}")

        return approval

    def is_plan_approved(self, plan_id: str, plan_content: str = None) -> bool:
        """
        Check if a plan is currently approved

        Args:
            plan_id: Plan ID to check
            plan_content: Optional plan content to verify hash

        Returns:
            True if approved and not expired, False otherwise
        """
        if plan_id not in self.registry["approved_plans"]:
            return False

        approval = self.registry["approved_plans"][plan_id]

        # Check expiration
        expires_at = datetime.fromisoformat(approval["expires_at"].replace("Z", ""))
        if datetime.utcnow() > expires_at:
            return False

        # Check status
        if approval.get("status") != "active":
            return False

        # Verify hash if content provided
        if plan_content:
            plan_hash = self._compute_plan_hash(plan_content)
            if plan_hash != approval["plan_hash"]:
                print(f"⚠️  Plan content changed! Hash mismatch.")
                print(f"   Expected: {approval['plan_hash']}")
                print(f"   Got: {plan_hash}")
                return False

        return True

    def revoke_plan(self, plan_id: str):
        """Revoke approval for a plan"""
        if plan_id not in self.registry["approved_plans"]:
            raise ValueError(f"Plan not found: {plan_id}")

        self.registry["approved_plans"][plan_id]["status"] = "revoked"

        # Add to audit log
        self.registry["audit_log"].append({
            "action": "revoke",
            "plan_id": plan_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        self._save_registry()
        print(f"🔴 Plan approval revoked: {plan_id}")

    def list_approved_plans(self):
        """List all approved plans"""
        if not self.registry["approved_plans"]:
            print("No approved plans.")
            return

        print("\n📋 Approved Plans:")
        print("=" * 80)

        now = datetime.utcnow()

        for plan_id, approval in self.registry["approved_plans"].items():
            status = approval.get("status", "active")
            expires_at = datetime.fromisoformat(approval["expires_at"].replace("Z", ""))
            expired = now > expires_at

            status_icon = {
                "active": "🟢" if not expired else "⏰",
                "revoked": "🔴",
                "expired": "⏰"
            }.get(status, "❓")

            print(f"\n{status_icon} {plan_id}")
            print(f"   Path: {approval.get('plan_path', 'N/A')}")
            print(f"   Hash: {approval['plan_hash']}")
            print(f"   Approved: {approval['approved_at']}")
            print(f"   Expires: {approval['expires_at']}")

            if expired:
                print(f"   Status: EXPIRED")
            else:
                time_left = expires_at - now
                hours_left = time_left.total_seconds() / 3600
                print(f"   Status: Active ({hours_left:.1f}h remaining)")

            if approval.get("note"):
                print(f"   Note: {approval['note']}")

    def enable_dangerous_skip(self, enabled: bool = True):
        """Enable/disable dangerous skip feature globally"""
        self.registry["settings"]["enable_dangerous_skip"] = enabled
        self._save_registry()

        if enabled:
            print("⚠️  Dangerous skip ENABLED")
            print("   Approved plans can now bypass sandbox restrictions")
        else:
            print("🔒 Dangerous skip DISABLED")
            print("   All commands will use sandbox")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Approve execution plans for dangerouslySkipPermissions"
    )
    parser.add_argument(
        "plan",
        nargs="?",
        help="Path to plan JSON file to approve"
    )
    parser.add_argument(
        "--expires",
        default="24h",
        help="Expiration time (e.g., 24h, 48h, 7d). Default: 24h"
    )
    parser.add_argument(
        "--note",
        default="",
        help="Optional note about this approval"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all approved plans"
    )
    parser.add_argument(
        "--revoke",
        metavar="PLAN_ID",
        help="Revoke approval for a plan"
    )
    parser.add_argument(
        "--enable-dangerous-skip",
        action="store_true",
        help="Enable dangerous skip feature globally"
    )
    parser.add_argument(
        "--disable-dangerous-skip",
        action="store_true",
        help="Disable dangerous skip feature globally"
    )

    args = parser.parse_args()

    manager = PlanApprovalManager()

    # List approved plans
    if args.list:
        manager.list_approved_plans()
        return

    # Revoke plan
    if args.revoke:
        manager.revoke_plan(args.revoke)
        return

    # Enable/disable dangerous skip
    if args.enable_dangerous_skip:
        manager.enable_dangerous_skip(True)
        return

    if args.disable_dangerous_skip:
        manager.enable_dangerous_skip(False)
        return

    # Approve plan
    if not args.plan:
        parser.print_help()
        return

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"❌ Plan file not found: {plan_path}")
        sys.exit(1)

    # Parse expiration time
    expires_str = args.expires.lower()
    if expires_str.endswith('h'):
        expires_hours = int(expires_str[:-1])
    elif expires_str.endswith('d'):
        expires_hours = int(expires_str[:-1]) * 24
    else:
        expires_hours = int(expires_str)

    manager.approve_plan(plan_path, expires_hours, args.note)

    # Show warning
    print("\n⚠️  WARNING:")
    print("   This plan can now execute Bash commands without sandboxing!")
    print("   To enable this feature, run:")
    print("   python approve-plan.py --enable-dangerous-skip")


if __name__ == "__main__":
    main()
