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
  sprintf('./MyOcean/Forecast/myov05-med-ingv-sal-an-fc-dm-%s.nc', target_date),
  level=1)
rasterTemperature <- raster(
  sprintf('./MyOcean/Forecast/myov05-med-ingv-tem-an-fc-dm-%s.nc', target_date),
  level=1)
rasterNitrate <- raster(
  sprintf('./MyOcean/Forecast/myov04-med-ogs-bio-an-fc-%s.nc', target_date),
  varname='nit',
  level=1)
rasterChlorofile <- raster(
  sprintf('MyOcean/Forecast/myov04-med-ogs-bio-an-fc-%s.nc', target_date),
  varname='chl',
  level=1)
rasterPhosphate <- raster(
  sprintf('MyOcean/Forecast/myov04-med-ogs-bio-an-fc-%s.nc', target_date),
  varname='pho',
  level=1)
rasterCurrX <- raster(
  sprintf('MyOcean/Forecast/myov05-med-ingv-cur-an-fc-dm-%s.nc', target_date),
  varname='vozocrtx',
  level=1)
rasterCurrY <- raster(
  sprintf('MyOcean/Forecast/myov05-med-ingv-cur-an-fc-dm-%s.nc', target_date),
  varname='vomecrty',
  level=1)

rasterSalinity.imputed <- imputeKNN(rasterSalinity)
rasterTemperature.imputed <- imputeKNN(rasterTemperature)
rasterNitrate.imputed <- imputeKNN(rasterNitrate)
rasterChlorofile.imputed <- imputeKNN(rasterChlorofile)
rasterPhosphate.imputed <- imputeKNN(rasterPhosphate)
rasterCurrX.imputed <- imputeKNN(rasterCurrX)
rasterCurrY.imputed <- imputeKNN(rasterCurrY)

# read points where we want to interpolate the data (beaches)
envBeaches <- read.table('Geo/beaches.txt', header=T, sep=",")
envBeaches[,c('lon', 'lat')]
xy <- SpatialPoints(envBeaches[,c('lon', 'lat')])

salinity.points <- extract(x=rasterSalinity.imputed, y=xy, method="bilinear")
temperature.points <- extract(x=rasterTemperature.imputed, y=xy, method="bilinear")
nitrate.points <- extract(x=rasterNitrate.imputed, y=xy, method="bilinear")
chlorofile.points <- extract(x=rasterChlorofile.imputed, y=xy, method="bilinear")
phosphate.points <- extract(x=rasterPhosphate.imputed, y=xy, method="bilinear")
currx.points <- extract(x=rasterCurrX.imputed, y=xy, method="bilinear")
curry.points <- extract(x=rasterCurrY.imputed, y=xy, method="bilinear")


data <- data.frame(
  lon = xy$lon[!is.na(salinity.points)],
  lat = xy$lat[!is.na(salinity.points)],
  salinity = salinity.points[!is.na(salinity.points)],
  temperature = temperature.points[!is.na(temperature.points)],
  nit = nitrate.points[!is.na(nitrate.points)],
  chlorophile = chlorofile.points[!is.na(chlorofile.points)],
  pho = phosphate.points[!is.na(phosphate.points)],
  currx = currx.points[!is.na(currx.points)],
  curry = currx.points[!is.na(curry.points)]
)

write.table(
  data,
  file=sprintf("./MyOcean/Forecast/Forecast_Env-%s.csv", target_date),
  row.names=FALSE, col.names=TRUE)
