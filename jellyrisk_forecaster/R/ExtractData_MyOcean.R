library(ncdf4)
library(raster)


# load the data in raster layers

rasterSalinity <- raster('MyOcean/myov04-med-ingv-sal-an-fc.nc')
rasterTemperature <- raster('MyOcean/myov04-med-ingv-tem-an-fc.nc', level=1)
rasterNitrate <- raster('MyOcean/myov04-med-ogs-bio-an-fc.nc', varname='nit')
rasterChlorofile <- raster('MyOcean/myov04-med-ogs-bio-an-fc.nc', varname='chl')
rasterPhosphate <- raster('MyOcean/myov04-med-ogs-bio-an-fc.nc', varname='pho')

xmin <- 0
xmax <- 5
ymin <- 39
ymax <- 44
e <- extent(xmin, xmax, ymin, ymax)

rasterSalinity.cropped <- crop(rasterSalinity, e)
rasterTemperature.cropped <- crop(rasterSalinity, e)
rasterNitrate.cropped <- crop(rasterNitrate, e)
rasterChlorofile.cropped <- crop(rasterChlorofile, e)
rasterPhosphate.cropped <- crop(rasterPhosphate, e)

# read points where we want to interpolate the data (beaches)
envBeaches <- read.table('Geo/beaches.txt', header=T)

xy <- SpatialPoints(envBeaches[,c('lon', 'lat')])

salinity.points <- extract(x=rasterSalinity.cropped, y=xy, method="bilinear")
temperature.points <- extract(x=rasterTemperature.cropped, y=xy, method="bilinear")
nitrate.points <- extract(x=rasterNitrate.cropped, y=xy, method="bilinear")
chlorofile.points <- extract(x=rasterChlorofile.cropped, y=xy, method="bilinear")
phosphate.points <- extract(x=rasterPhosphate.cropped, y=xy, method="bilinear")


data <- data.frame(
  lon = xy$lon[!is.na(salinity.points)],
  lat = xy$lat[!is.na(salinity.points)],
  sal = salinity.points[!is.na(salinity.points)],
  sstmean = temperature.points[!is.na(temperature.points)],
  nit = nitrate.points[!is.na(nitrate.points)],
  chlomean = chlorofile.points[!is.na(chlorofile.points)],
  pho = phosphate.points[!is.na(phosphate.points)]
)

write.table(data, file="MyOcean/predictionData.csv", row.names=FALSE, col.names=TRUE)
