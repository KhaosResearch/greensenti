import typer

from greensenti.cli.compute_index import app as compute_index_group
from greensenti.cli.dhus import app as dhus_group
from greensenti.cli.raster import app as raster_group

app = typer.Typer()

app.add_typer(dhus_group, name="dhus", help="DHUS access and download.")
app.add_typer(compute_index_group, name="compute-index", help="Compute a plethora of remote sensing indexes.")
app.add_typer(raster_group, name="raster", help="Raster operations.")

if __name__ == "__main__":
    app()
