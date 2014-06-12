setwd("~/GuloGulo/proj_t2050")

ensembleResultsRL <- raster('proj_t2050_GuloGulo_ensemble.grd')
ensembleResultsXY <- xyFromCell(object=ensembleResultsRL, 
                       cell=which(ensembleResultsRL[]>0))

ensembleResults <- extract(x=ensembleResultsRL, y=ensembleResultsXY)

data <- data.frame(
	lon=ensembleResultsXY[,1],
	lat=ensembleResultsXY[,2],
	prob=ensembleResults
)



###

myBiomodEMProjection <- BIOMOD_Projection(
                         modeling.output = myBiomodEM,
                         new.env = myExpl,
                         proj.name = 'current',
                         selected.models = 'all',
                         binary.meth = 'ROC',
                         compress = 'xz',
                         clamping.mask = F)