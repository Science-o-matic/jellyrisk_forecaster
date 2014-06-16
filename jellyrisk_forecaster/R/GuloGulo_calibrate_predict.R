### Encoding: UTF-8

###################################################
### 1: Load options and data
###################################################

options(prompt = " ", continue = "  ", width = 60, digits=4)
.CurFileName <- "biomod2_getting_started"
# .PrefixName <- strsplit(.CurFileName, "\\.")[[1]][1]
.PrefixName <- .CurFileName
.RversionName <- R.version.string
.PkgVersion <- packageDescription("biomod2")$Version


# load the library
library(biomod2)

# load our species raster
myResp.ras <- raster( system.file(
                        "external/species/GuloGulo.grd", 
                        package="biomod2") )

# extract the presences data

# the name
myRespName <- 'GuloGulo'

# the XY coordinates of the presence
myRespXY <- xyFromCell(object=myResp.ras, 
                       cell=which(myResp.ras[]>0))

# and the presence data 
myResp <- extract(x=myResp.ras, y=myRespXY)

# load the environmental raster layers

# Environmental variables extracted from Worldclim (bio_3, bio_4, 
# bio_7, bio_11 & bio_12)
myExpl = stack( system.file( "external/bioclim/current/bio3.grd", 
                             package="biomod2"),
                system.file( "external/bioclim/current/bio4.grd", 
                             package="biomod2"), 
                system.file( "external/bioclim/current/bio7.grd", 
                             package="biomod2"),  
                system.file( "external/bioclim/current/bio11.grd", 
                             package="biomod2"), 
                system.file( "external/bioclim/current/bio12.grd", 
                             package="biomod2"))

# format data
myBiomodData <- BIOMOD_FormatingData(resp.var = myResp,
                                     expl.var = myExpl,
                                     resp.xy = myRespXY,
                                     resp.name = myRespName,
                                     PA.nb.rep = 2,
                                     PA.nb.absences = 200,
                                     PA.strategy = 'random')


###################################################
### 2. Define Models Options using default options.
###################################################

myBiomodOption <- BIOMOD_ModelingOptions()


###################################################
### 3. Compute the models 
###################################################

myBiomodModelOut <- BIOMOD_Modeling( 
                           myBiomodData, 
                           models = c('SRE','CTA','RF','MARS','FDA'), 
                           models.options = myBiomodOption, 
                           NbRunEval=1, 
                           DataSplit=80, 
                           Yweights=NULL, 
                           VarImport=3, 
                           models.eval.meth = c('TSS','ROC'),
                           SaveObj = TRUE,
                           rescal.all.models = TRUE)


###################################################
### 4. Ensemble modelling
###################################################

myBiomodEM <- BIOMOD_EnsembleModeling( 
                     modeling.output = myBiomodModelOut,
                     chosen.models = 'all',
                     eval.metric = c('TSS'),
                     eval.metric.quality.threshold = c(0.85),
                     prob.mean = T,
                     prob.cv = T,
                     prob.ci = T,
                     prob.ci.alpha = 0.05,
                     prob.median = T,
                     committee.averaging = T,
                     prob.mean.weight = T,
                     prob.mean.weight.decay = 'proportional' )



###################################################
### 5. Future projections
###################################################

# load environmental variables for the future. 
myExpl2050 = stack( system.file( "external/bioclim/future/bio3.grd",
                                 package="biomod2"),
                    system.file( "external/bioclim/future/bio4.grd",
                                 package="biomod2"),
                    system.file( "external/bioclim/future/bio7.grd",
                                 package="biomod2"),
                    system.file( "external/bioclim/future/bio11.grd",
                                 package="biomod2"),
                    system.file( "external/bioclim/future/bio12.grd",
                                 package="biomod2"))

myBiomomodProj2050 <- BIOMOD_Projection(
                              modeling.output = myBiomodModelOut,
                              new.env = stack(myExpl2050),
                              proj.name = 't2050',
                              selected.models = 'all',
                              binary.meth = 'ROC',
                              compress = 'xz',
                              clamping.mask = T)
                              


###################################################
### 6. Ensemble forecasting
###################################################

# This saves the file $pwd/GuloGulo/proj_t2050/proj_t2050_GuloGulo_ensemble.grd
myBiomodEF <- BIOMOD_EnsembleForecasting( 
                      projection.output = myBiomomodProj2050,
                      EM.output = myBiomodEM )


###################################################
### 7. Save data to CSV file
###################################################

EFResultsRL <- raster('GuloGulo/proj_t2050/proj_t2050_GuloGulo_ensemble.grd')
EFResultsXY <- xyFromCell(object=EFResultsRL, 
                       cell=which(EFResultsRL[]>0))

EFResults <- extract(x=EFResultsRL, y=EFResultsXY)

data <- data.frame(
  lon=EFResultsXY[,1],
  lat=EFResultsXY[,2],
  prob=EFResults
)

write.csv(data, file="GuloGuloEF.csv", row.names=FALSE)