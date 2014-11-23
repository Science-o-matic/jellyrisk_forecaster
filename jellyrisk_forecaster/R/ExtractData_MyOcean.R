library(raster)
library(FNN)

target_date <- commandArgs(trailingOnly=TRUE)[1]

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

rasterSalinity <- raster(
  sprintf('./MyOcean/Forecast/myov04-med-ingv-sal-an-fc-%s.nc', target_date),
  level=1)
rasterTemperature <- raster(
  sprintf('./MyOcean/Forecast/myov04-med-ingv-tem-an-fc-%s.nc', target_date),
  level=1)
rasterCurrX <- raster(
  sprintf('MyOcean/Forecast/myov04-med-ingv-cur-an-fc-%s.nc', target_date),
  varname='vozocrtx',
  level=1)
rasterCurrY <- raster(
  sprintf('MyOcean/Forecast/myov04-med-ingv-cur-an-fc-%s.nc', target_date),
  varname='vomecrty',
  level=1)

rasterSalinity.imputed <- imputeKNN(rasterSalinity)
rasterTemperature.imputed <- imputeKNN(rasterTemperature)
rasterCurrX.imputed <- imputeKNN(rasterCurrX)
rasterCurrY.imputed <- imputeKNN(rasterCurrY)

# read points where we want to interpolate the data (beaches)
envBeaches <- read.table('Geo/beaches.txt', header=T)

xy <- SpatialPoints(envBeaches[,c('lon', 'lat')])

salinity.points <- extract(x=rasterSalinity.imputed, y=xy, method="bilinear")
temperature.points <- extract(x=rasterTemperature.imputed, y=xy, method="bilinear")
currx.points <- extract(x=rasterCurrX.imputed, y=xy, method="bilinear")
curry.points <- extract(x=rasterCurrY.imputed, y=xy, method="bilinear")

data <- data.frame(
  lon=xy$lon[!is.na(salinity.points)],
  lat=xy$lat[!is.na(salinity.points)],
  vosaline=salinity.points[!is.na(salinity.points)],
  votemper=temperature.points[!is.na(temperature.points)],
  vozocrtx=currx.points[!is.na(currx.points)],
  vomecrty=currx.points[!is.na(curry.points)]
)

write.table(
  data,
  file=sprintf("./MyOcean/Forecast/Forecast_Env-%s.csv", target_date),
  row.names=FALSE, col.names=TRUE)
