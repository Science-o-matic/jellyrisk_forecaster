# Load raster brick of monthly mean temperatures from MyOcean from May 2007
# to Oct 2010 and extract the values for each month at the selected beaches

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

# brick with mean temperatures from may 2007 to october 2010, month by month
# MEDSEA_REANALYSIS_PHYS_006_004??
brickTemperature <- brick('./MyOcean/myov04-med-ingv-tem-rean-mm_2007-2010.nc')

# table with equivalences between layer number, month and year in previous file
layer_month_year <- read.csv('./MyOcean/layer_month_year.csv', sep='\t')


# save all temperatures by month and beach
allTemperatures <- data.frame()


# read points where we want to interpolate the data (beaches)
envBeaches <- read.table('Geo/beaches.txt', header=T)

for (i in 1:nlayers(brickTemperature)) {
  layer <- raster(brickTemperature, layer=i)
  layer.imputed <- imputeKNN(layer)

  xy <- SpatialPoints(envBeaches[,c('lon', 'lat')])
  temperature.points <- extract(x=layer.imputed, y=xy, method="bilinear")

  new_temperatures <- data.frame(
    beach=1:length(temperature.points),
    month=layer_month_year[i,]$month,
    year=layer_month_year[i,]$year,
    temperature=temperature.points
  )
  allTemperatures <- rbind(allTemperatures, new_temperatures)
}


# Load daily medusae inspections from from May 2007 to Oct 2010 and aggregate
# (sum) them broken by beach, month and year.

# The aggregation is done to gain statistical significance, since it is
# quite normal that no medusae are detected on a given day even if the
# conditions are favorable.

data <- read.csv("./DailyInspections/Jellyfish_Inspectors_Daily_2007-2010.csv", sep="\t")

cum_pelagia_by_beach_month_year <- aggregate( Pelagia ~ Site_ID + month + year, data, sum)
names(cum_pelagia_by_beach_month_year)[1] <- "beach"


# Merge environmental, geographical and presence dataframes
historical_data <- merge(envBeaches, merge(allTemperatures, cum_pelagia_by_beach_month_year))

write.table(historical_data,
            file="./historical-data-by-beach-2007-2010.csv",
            row.names=FALSE, col.names=TRUE)
