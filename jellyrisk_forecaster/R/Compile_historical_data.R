# Load raster brick of monthly mean temperatures from MyOcean from May 2007
# to Oct 2010 and extract the values for each month at the selected beaches

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

# brick with mean variables from may 2007 to october 2010, month by month
# MEDSEA_REANALYSIS_PHYS_006_004
brickTemperature <- brick('./MyOcean/Historical/myov04-med-ingv-tem-rean-mm_2007-2010.nc', level=1)
brickSalinity <- brick('./MyOcean/Historical/myov04-med-ingv-sal-rean-mm_2007-2010.nc', level=1)
# MEDSEA_REANALYSIS_BIO_006_007
brickChlorophile <- brick('./MyOcean/Historical/myov04-med-ogs-bio-rean_2007-2010.nc', varname='chl', level=1)
brickCurrX <- brick('./MyOcean/Historical/myov04-med-ingv-cur-rean-mm_2007-2010.nc', varname='vozocrtx', level=1)
brickCurrY <- brick('./MyOcean/Historical/myov04-med-ingv-cur-rean-mm_2007-2010.nc', varname='vomecrty', level=1)


# table with equivalences between layer number, month and year in previous file
layer_month_year <- read.csv('./MyOcean/layer_month_year.csv')


# save all variables by month and beach
allVariables <- data.frame()


# read points where we want to interpolate the data (beaches)
envBeaches <- read.table('Geo/beaches.txt', header=T)
xy <- SpatialPoints(envBeaches[,c('lon', 'lat')])

for (i in 1:nlayers(brickTemperature)) {
  layer_temperature <- raster(brickTemperature, layer=i)
  layer_salinity <- raster(brickSalinity, layer=i)
  layer_chlorophile <- raster(brickChlorophile, layer=i)
  layer_currx <- raster(brickCurrX, layer=i)
  layer_curry <- raster(brickCurrY, layer=i)

  layer_temperature.imputed <- imputeKNN(layer_temperature)
  layer_salinity.imputed <- imputeKNN(layer_salinity)
  layer_chlorophile.imputed <- imputeKNN(layer_chlorophile)
  layer_currx.imputed <- imputeKNN(layer_currx)
  layer_curry.imputed <- imputeKNN(layer_curry)

  temperature.points <- extract(x=layer_temperature.imputed, y=xy, method="bilinear")
  salinity.points <- extract(x=layer_salinity.imputed, y=xy, method="bilinear")
  chlorophile.points <- extract(x=layer_chlorophile.imputed, y=xy, method="bilinear")
  currx.points <- extract(x=layer_currx.imputed, y=xy, method="bilinear")
  curry.points <- extract(x=layer_curry.imputed, y=xy, method="bilinear")

  new_variables <- data.frame(
    beach=1:length(temperature.points),
    month=layer_month_year[i,]$month,
    year=layer_month_year[i,]$year,
    temperature=temperature.points,
    salinity=salinity.points,
    chlorophile=chlorophile.points,
    currx=currx.points,
    curry=curry.points
  )
  allVariables <- rbind(allVariables, new_variables)
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
historical_data <- merge(envBeaches, merge(allVariables, cum_pelagia_by_beach_month_year))

write.table(historical_data,
            file="./MyOcean/Historical/historical-data-by-beach-2007-2010.csv",
            row.names=FALSE, col.names=TRUE)
