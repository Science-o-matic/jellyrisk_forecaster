library(ncdf4)
library(raster)


# load the data in raster layers

rasterSalinity <- raster('myov04-med-ingv-sal-an-fc.nc')
rasterTemperature <- raster('myov04-med-ingv-tem-an-fc.nc', level=1)
rasterNitrate <- raster('myov04-med-ogs-bio-an-fc.nc', varname='nit')
rasterChlorofile <- raster('myov04-med-ogs-bio-an-fc.nc', varname='chl')
rasterPhosphate <- raster('myov04-med-ogs-bio-an-fc.nc', varname='pho')

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
envCatalonia <- read.table('data/Env.points.Catalonia.txt', header=T)

xy <- SpatialPoints(envCatalonia[,c('Long', 'lat')])

salinity.points <- extract(x=rasterSalinity.cropped, y=xy, method="bilinear")
temperature.points <- extract(x=rasterTemperature.cropped, y=xy, method="bilinear")
nitrate.points <- extract(x=rasterNitrate.cropped, y=xy, method="bilinear")
chlorofile.points <- extract(x=rasterChlorofile.cropped, y=xy, method="bilinear")
phosphate.points <- extract(x=rasterPhosphate.cropped, y=xy, method="bilinear")


data <- data.frame(
  lon=xy[!is.na(salinity.points),'Long'],
  lat=xy[!is.na(salinity.points),'lat'],
  Salinity=salinity.points[!is.na(salinity.points)],
  sstmax=temperature.points[!is.na(temperature.points)],
  nitrate=nitrate.points[!is.na(nitrate.points)],
  chlomax=chlorofile.points[!is.na(chlorofile.points)],
  phosphate=phosphate.points[!is.na(phosphate.points)]
)

write.table(data, file="predictionData.txt", row.names=FALSE)
