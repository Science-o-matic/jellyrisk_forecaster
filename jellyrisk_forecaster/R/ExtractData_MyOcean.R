library(ncdf4)
library(raster)
library(FNN)

imputeKNN <- function(raster_layer) {
    values <- getValues(raster_layer)
    xy <- xyFromCell(raster_layer, 1:ncell(raster_layer))

    missing <- is.na(values)
    present <- !missing

    missing_values <- values[missing]
    present_values <- values[present]

    neighs <- get.knnx(xy[present,], xy[missing,], k=1)

    new_values <- values
    new_values[missing] <- present_values[neighs$nn.index]

    new_raster_layer <- raster_layer
    new_raster_layer[] <- new_values

    return(new_raster_layer)
}

# load the data in raster layers

rasterSalinity <- raster('MyOcean/myov04-med-ingv-sal-an-fc.nc')
rasterTemperature <- raster('MyOcean/myov04-med-ingv-tem-an-fc.nc', level=1)
rasterNitrate <- raster('MyOcean/myov04-med-ogs-bio-an-fc.nc', varname='nit')
rasterChlorofile <- raster('MyOcean/myov04-med-ogs-bio-an-fc.nc', varname='chl')
rasterPhosphate <- raster('MyOcean/myov04-med-ogs-bio-an-fc.nc', varname='pho')

rasterSalinity.imputed <- imputeKNN(rasterSalinity)
rasterTemperature.imputed <- imputeKNN(rasterTemperature)
rasterNitrate.imputed <- imputeKNN(rasterNitrate)
rasterChlorofile.imputed <- imputeKNN(rasterChlorofile)
rasterPhosphate.imputed <- imputeKNN(rasterPhosphate)

# read points where we want to interpolate the data (beaches)
envBeaches <- read.table('Geo/beaches.txt', header=T)

xy <- SpatialPoints(envBeaches[,c('lon', 'lat')])

salinity.points <- extract(x=rasterSalinity.imputed, y=xy, method="bilinear")
temperature.points <- extract(x=rasterTemperature.imputed, y=xy, method="bilinear")
nitrate.points <- extract(x=rasterNitrate.imputed, y=xy, method="bilinear")
chlorofile.points <- extract(x=rasterChlorofile.imputed, y=xy, method="bilinear")
phosphate.points <- extract(x=rasterPhosphate.imputed, y=xy, method="bilinear")


data <- data.frame(
  lon = xy$lon[!is.na(salinity.points)],
  lat = xy$lat[!is.na(salinity.points)],
  sal = salinity.points[!is.na(salinity.points)],
  temperature = temperature.points[!is.na(temperature.points)],
  nit = nitrate.points[!is.na(nitrate.points)],
  chlomean = chlorofile.points[!is.na(chlorofile.points)],
  pho = phosphate.points[!is.na(phosphate.points)]
)

write.table(data, file="MyOcean/predictionData.csv", row.names=FALSE, col.names=TRUE)
