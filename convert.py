import os
from uuid import uuid4
import glob

from osgeo import gdal



result_dir = "COGs"

geotiff_dir = "tiffs"

if not os.path.exists(result_dir):
      os.makedirs(result_dir)
      print("Created directory for COGs!")
else:
    print("Cogs directory already exists!")


# Loop through all .tif files in subdirectories
# and reproject them to COG format
# Note: Ensure that the script is run in a directory containing subdirectories with .tif files
for path in glob.iglob(f"{geotiff_dir}/*.tif"):
    path.split("/")[1]

    # Defining the output COG filename
    Gtiff_filename = path.split("/")[1]
    # only reproject files that do not already have the suffix "_reprojected.tif"
    # This avoids reprocessing files that have already been converted
    # to COG format
    print(f"Processing file: {Gtiff_filename}")
    if not Gtiff_filename.endswith("_reprojected.tif"):
        ds = gdal.Open(path)
        tmp_ds = f"/vsimem/{uuid4().hex}.tif"

        # read the raster data
        data = ds.GetRasterBand(1).ReadAsArray()
        print(ds.GetGeoTransform())
        # get the size of the image
        size_y, size_x = data.shape

        # create a GeoTiff file
        driver = gdal.GetDriverByName("GTiff")

        out_ds = driver.Create(tmp_ds, size_x, size_y, 1, gdal.GDT_Int16)

        if out_ds is None:
            print("Could not create output file '%s'." % tmp_ds)
        else:
            # set the geospatial metadata, no data value, and description
            # for the output dataset

            proj = "EPSG:4326"

            out_ds.SetGeoTransform(ds.GetGeoTransform())

            out_ds.GetRasterBand(1).SetNoDataValue(ds.GetRasterBand(1).GetNoDataValue())

            out_ds.GetRasterBand(1).SetDescription(ds.GetRasterBand(1).GetDescription())
            out_ds.SetProjection(proj)

            out_ds.GetRasterBand(1).WriteArray(data)

        gdal.GetDriverByName("GTiff").CreateCopy(tmp_ds, out_ds)


        print(f"Reprojected data written to {tmp_ds}")

        cog_filename = f"COGs/{Gtiff_filename.replace(".tif", "_reprojected_4326_COG.tif")}"


        # Convert the temporary GeoTIFF to COG format
        # using the GDAL Translate function
        # with appropriate creation options for COG
        gdal.Translate(
            cog_filename,
            tmp_ds,
            format="COG",
            creationOptions=["COMPRESS=DEFLATE", "PREDICTOR=2"],
        )


        print(f"Converted {Gtiff_filename} to COG format: {cog_filename}")
        # Clean up temporary files
        gdal.Unlink(tmp_ds)
        out_ds.FlushCache()

        ds = None
        out_ds = None
