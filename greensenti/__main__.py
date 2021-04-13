import typer

from greensenti.cli.compute_index import app as compute_index_grup
from greensenti.cli.download_products import dhus_download
from greensenti.cli.product import app as product_group
from greensenti.cli.raster import app as raster_group

app = typer.Typer()
app.command()(dhus_download)
app.add_typer(compute_index_grup, name="compute-index", help="Compute a plethora of remote sensing indexes.")
app.add_typer(raster_group, name="raster", help="Raster operations.")
app.add_typer(product_group, name="product", help="Manage product storage.")

if __name__ == "__main__":
    app()
