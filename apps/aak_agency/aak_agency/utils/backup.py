"""
aak_agency.utils.backup
─────────────────────────
Daily S3 backup triggered by the Frappe scheduler.
Backs up the site's database + files to s3://{S3_BUCKET}/backups/{site}/{date}/
"""

import os
import frappe
from frappe.utils import today


def run_s3_backup():
    """
    Called daily by hooks.py scheduler_events.
    Runs bench backup and uploads to S3.
    """
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        frappe.log_error("boto3 not installed — S3 backup skipped.", "S3 Backup")
        return

    bucket = os.environ.get("S3_BUCKET", "")
    region = os.environ.get("AWS_REGION", "ap-south-1")

    if not bucket:
        frappe.log_error("S3_BUCKET env var not set — backup skipped.", "S3 Backup")
        return

    site = frappe.local.site
    backup_path = frappe.utils.get_bench_path() + f"/sites/{site}/private/backups"

    # Trigger bench backup
    frappe.utils.execute_in_shell(f"bench --site {site} backup --with-files")

    # Upload all new backup files to S3
    s3 = boto3.client("s3", region_name=region)
    date_prefix = today()
    uploaded = []

    for filename in os.listdir(backup_path):
        if filename.endswith((".sql.gz", ".tar", ".tar.gz")):
            local_path = os.path.join(backup_path, filename)
            s3_key = f"backups/{site}/{date_prefix}/{filename}"
            try:
                s3.upload_file(local_path, bucket, s3_key)
                uploaded.append(s3_key)
            except (BotoCoreError, ClientError) as exc:
                frappe.log_error(str(exc), "S3 Backup Upload Error")

    if uploaded:
        frappe.logger().info(f"[S3 Backup] Uploaded {len(uploaded)} files for {site} on {date_prefix}")
    else:
        frappe.log_error("No backup files found to upload.", "S3 Backup")
