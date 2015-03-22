library(raster)
library(FNN)

imputeKNN <- function(raster_layer) {
  # fill NAs in the raster layer with the closest value
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


# read input args
args = commandArgs(trailingOnly=TRUE)
beaches_filepath = args[1]
nc_filepath = args[2]
var = args[3]
out_filepath = args[4]

all_layers <- data.frame()

# read points where we want to interpolate the data (beaches)
envBeaches <- read.table(beaches_filepath, header=T, sep=',')
xy <- SpatialPoints(envBeaches[,c('lon', 'lat')])

my_brick <- brick(nc_filepath, varname=var, level=1)

# each layer corresponds to a day
for (i in 1:nlayers(my_brick)) {
  layer <- raster(my_brick, layer=i)
  layer.imputed <- imputeKNN(layer)  # avoid getting NAs in beaches
  points <- extract(x=layer.imputed, y=xy, method="bilinear")

  Point.date = substr(names(layer), 2, 11)
  print(Point.date)

  new_layer <- data.frame(
    Site_ID=envBeaches['beach'],
    lon=envBeaches['lon'],
    lat=envBeaches['lat'],
    Point.date=Point.date,
    var=points
  )
  names(new_layer) <- c('Site_ID', 'lon', 'lat', 'Point.date', var)

  # write header for first row
  if (i==1) {
    write.table(new_layer, file=out_filepath, row.names=FALSE, col.names=TRUE, sep=',')
  }
  else {
    write.table(new_layer, file=out_filepath, row.names=FALSE, col.names=FALSE, sep=',', append=TRUE)
  }
}
