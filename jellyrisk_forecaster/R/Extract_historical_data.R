library(raster)
library(FNN)
library(date)

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
start_date = args[1]
end_date = args[2]
nc_filepath = args[3]
var = args[4]
out_filepath = args[5]

all_layers <- data.frame()

# read points where we want to interpolate the data (beaches)
envBeaches <- read.table('Geo/beaches.txt', header=T)
xy <- SpatialPoints(envBeaches[,c('lon', 'lat')])

my_brick <- brick(nc_filepath, varname=var, level=1)

my_start_date = strsplit(as.character(start_date), '-')
my_start_date.julian = mdy.date(
  as.integer(my_start_date[[1]][2]),
  as.integer(my_start_date[[1]][3]),
  as.integer(my_start_date[[1]][1])
)

# each layer corresponds to a day
for (i in 1:nlayers(my_brick)) {
  current_julian_date = my_start_date.julian + (i-1)
  current_date = date.mdy(current_julian_date)

  layer <- raster(my_brick, layer=i)
  layer.imputed <- imputeKNN(layer)  # avoid getting NAs in beaches
  points <- extract(x=layer.imputed, y=xy, method="bilinear")

  new_layer <- data.frame(
    Site_ID=1:length(points),
    day=current_date$day,
    month=current_date$month,
    year=current_date$year,
    var=points
  )
  names(new_layer) <- c('Site_ID', 'day', 'month', 'year', var)
  all_layers <- rbind(all_layers, new_layer)
}

write.table(all_layers, file=out_filepath, row.names=FALSE, col.names=TRUE, sep='\t')
