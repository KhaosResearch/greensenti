import json
import os
from pathlib import Path

import typer
from minio import Minio

from greensenti.settings import settings

app = typer.Typer()


@app.command()
def get_product(
    title: str = typer.Argument(..., help="Product name"),
    output: Path = typer.Option(Path("./"), exists=True, dir_okay=True, help="Output folder"),
):
    """
    Downloads product data from remote storage to output folder.
    """
    # download data to product data dir
    client = Minio(
        endpoint=f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
    )

    objs = client.list_objects(bucket_name=title)

    with typer.progressbar(objs) as progress:
        for obj in progress:
            typer.echo(f"downloading {obj.object_name}")

            dest = Path(output, title, obj.object_name)
            client.fget_object(
                bucket_name=title,
                object_name=obj,
                file_path=dest,
            )


@app.command()
def upload_product(
    title: str = typer.Argument(..., help="Product name"),
    folder: str = typer.Argument(..., exists=True, dir_okay=True, help="Product folder"),
    bucket: str = typer.Option(..., help="Destination bucket name"),
):
    """
    Uploads product's data to remote directory.
    """
    # upload data to product data dir
    client = Minio(
        endpoint=f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
    )

    # find data in folder
    files = []
    for file in os.listdir(folder):
        files.append(file)

    policy_read_only = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Deny",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{title}/*",
            }
        ],
    }
    client.make_bucket(title)
    client.set_bucket_policy(title, json.dumps(policy_read_only))

    with typer.progressbar(files) as progress:
        for obj in progress:
            typer.echo(f"uploading {obj}")

            output = Path(bucket, os.path.basename(obj))
            client.fput_object(
                bucket_name=title,
                object_name=obj,
                file_path=output,
            )
