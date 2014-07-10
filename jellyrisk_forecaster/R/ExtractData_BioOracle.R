#------------------------------------------------------------------#
# Bio-ORACLE - RASTER
#------------------------------------------------------------------#
# setwd("E:/PAPERS/PhD - THESIS/SDM - Antonio/ACA/DatosR/MODELS_BIORACLE/EJEMPLOS ANTIGUOS")
# getwd()
#------------------------------------------------------------------#
# load("Raster.Bioracle.RData")

# save.image("Raster.Bioracle.RData")

# rm(list=ls())

# q(save="no")
#------------------------------------------------------------------#
#------------------------------------------------------------------#
library("raster")
library("rgdal")

e <- extent(-9.5, 37.0, 29.667, 46.4691)

#------------------------------------------------------------------#
#Cargamos salinidad, hacemos el crop y guaradmos como .grd #
#------------------------------------------------------------------#
salinity <- raster("BioOracle/salinity.asc")

# salinitymed <- crop(salinity, e)


# writeRaster(salinitymed, "BioOracle/salinitymed.grd")
# #------------------------------------------------------------------#



#------------------------------------------------------------------#
#Cargamos sstmean, hacemos el crop y guaradmos como .grd #
#------------------------------------------------------------------#
sstmean <- raster("BioOracle/sstmean.asc")

# sstmeanmed <- crop(sstmean, e)


# writeRaster(sstmeanmed, "BioOracle/sstmeanmed.grd")
# #------------------------------------------------------------------#

#------------------------------------------------------------------#
#Cargamos phosphate, hacemos el crop y guaradmos como .grd #
#------------------------------------------------------------------#
phos <- raster("BioOracle/phos.asc")


# phosmed <- crop(phos, e)

# writeRaster(phosmed, "phosphatemed.grd")
# #------------------------------------------------------------------#


#------------------------------------------------------------------#
#Cargamos CHLA, hacemos el crop y guaradmos como .grd #
#------------------------------------------------------------------#
chlomean <- raster("BioOracle/chlomean.asc")

# chlomeanmed <- crop(chlomean, e)

# writeRaster(chlomeanmed, "chlomeanmed.grd")
# #------------------------------------------------------------------#


#------------------------------------------------------------------#
#Cargamos NITRATE, hacemos el crop y guaradmos como .grd #
#------------------------------------------------------------------#
nitrate <- raster("BioOracle/nitrate.asc")

# nitratemed <- crop(nitrate, e)

# writeRaster(nitratemed, "nitratemed.grd")
# #------------------------------------------------------------------#


#------------------------------------------------------------------#
#Cargamos PHOSPHATE, hacemos el crop y guaradmos como .grd #
#------------------------------------------------------------------#
dissox <- raster("BioOracle/dissox.asc")

# dissoxmed <- crop(dissox, e)

# writeRaster(dissoxmed, "dissoxmed.grd")
# #------------------------------------------------------------------#



# OBTENER LOS VALORES AMBIENTALES PARA MIS PUNTOS




#------------------------------------------------------------------#
# EXTRAIGO LOS VALORES AMBIENTALES PARA LAS PLAYAS CATALANAS
#------------------------------------------------------------------#
#------------------------------------------------------------------#
#------------------------------------------------------------------#
# Tengo que crear una matriz con los puntos.
puntos.beaches <- read.table("Geo/beaches.txt", header=T, dec=".")

I1 <- is.na(puntos.beaches$lon) & is.na(puntos.beaches$lat)

coord.beaches <- puntos.beaches[!I1, ]

coord.beaches <- SpatialPoints(coord.beaches)

#------------------------------------------------------------------#
# Obtengo los valores de la Capa RASTER para las coordenadas definidas anteriormente

# Salinidad
salinity.points.beaches <- extract(x=salinity, y=coord.beaches, method="bilinear")


#sstmean
sstmean.points.beaches <- extract(x=sstmean, y=coord.beaches, method="bilinear")

#nitrate
nitrate.points.beaches <- extract(x=nitrate, y=coord.beaches, method="bilinear")

#dissox
dissox.points.beaches <- extract(x=dissox, y=coord.beaches, method="bilinear")

#chlomean
chlomean.points.beaches <- extract(x=chlomean, y=coord.beaches, method="bilinear")

#phosphate
phosphate.points.beaches <- extract(x=phos, y=coord.beaches, method="bilinear")

#------------------------------------------------------------------#

env.point.beaches <- data.frame(
    lon = coord.beaches$lon,
    lat = coord.beaches$lat,
    sal = salinity.points.beaches,
    sstmean = sstmean.points.beaches,
    nit = nitrate.points.beaches,
    dissox = dissox.points.beaches,
    chlomean = chlomean.points.beaches,
    pho = phosphate.points.beaches
)

#------------------------------------------------------------------#
#Guardando el archivo
write.table(env.point.beaches, file="BioOracle/Env.Points.Beaches.csv",quote=F, sep="\t", na = "NA", dec= ".", col.names=T, row.names=FALSE)
