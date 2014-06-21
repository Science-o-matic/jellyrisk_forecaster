#------------------------------------------------------------------#
# ACA Acumulado - Bio-ORACLE -- biomod2 - PELAGIA NOCTILUCA
#------------------------------------------------------------------#
setwd("E:/PAPERS/PhD - THESIS/SDM - Antonio/ACA/DatosR/MODELS_BIORACLE/Acum.Env.ACA")
getwd()
#------------------------------------------------------------------#
load("Aca.acum.Bioracle.Pnoctiuca.RData")

save.image("Aca.acum.Bioracle.Pnoctiuca.RData")

rm(list=ls())

q(save="no")
#------------------------------------------------------------------#
#------------------------------------------------------------------#
library("biomod2")
library("ggplot2")
library("ggmap")

#------------------------------------------------------------------#
#Load the presence of the species
DataSpecies <- read.table("Acum.Env.ACA.txt", header=T, dec=",")

head(DataSpecies)

#------------------------------------------------------------------#
#------------------------------------------------------------------#
# PELAGIA NOCTILUCA
#------------------------------------------------------------------#
#------------------------------------------------------------------#
# the name of studied species
myRespName.pn <- "Pelagia.noctiluca"

#------------------------------------------------------------------#
# the presence/absences data for our species
myResp.pn <- as.numeric(DataSpecies[,myRespName.pn])

#------------------------------------------------------------------#
# the XY coordinates of species data
myRespXY <- DataSpecies[,c("Long","lat")]

#------------------------------------------------------------------#
# Environmental variables
myExpl <- DataSpecies[,c("Salinity","sstmax","nitrate", "dissox", "chlomax", "phosphate")]

windows()
level.plot(data.in=myResp.pn, XY=myRespXY, color.gradient = "red", cex = 1, level.range = c(min(myResp.pn), max(myResp.pn)), show.scale = TRUE, title = "Pelagia noctiluca", SRC=FALSE, save.file="no", ImageSize="large", AddPresAbs=NULL)

#------------------------------------------------------------------#
# Formateando para Biomod
myBiomodData.pn <- BIOMOD_FormatingData(resp.var = myResp.pn,
                                        expl.var = myExpl,
                                        resp.xy = myRespXY,
                                        resp.name = myRespName.pn)

#------------------------------------------------------------------#
# check whether the data are correctly formatted
myBiomodData.pn

windows()
plot(myBiomodData.pn)
#------------------------------------------------------------------#
# Defining Models Options using default options.
myBiomodOption <- BIOMOD_ModelingOptions()

#------------------------------------------------------------------#
#------------------------------------------------------------------#
# Computing the models
myBiomodModelOut.pn <- BIOMOD_Modeling(myBiomodData.pn,
                        models = c("GLM", "GAM", "CTA","RF","MARS"),
                        models.options = myBiomodOption,
                        NbRunEval=3,
                        DataSplit=80,
                        Prevalence=0.5,
                        VarImport=3,
                        models.eval.meth = c('TSS','ROC'),
                        SaveObj = TRUE,
                        rescal.all.models = TRUE,
                        do.full.models = FALSE,
                        modeling.id = paste(myRespName.pn,"FirstModeling",sep=""))

#------------------------------------------------------------------#
# have a look at some outputs:  modeling summary
myBiomodModelOut.pn

#------------------------------------------------------------------#
# have a look at some outputs: models evaluations
## get all models evaluation
myBiomodModelEval.pn <- getModelsEvaluations(myBiomodModelOut.pn)

#------------------------------------------------------------------#
## print the dimnames of this object
dimnames(myBiomodModelEval.pn)

#------------------------------------------------------------------#
# let's print the TSS scores of Random Forest
myBiomodModelEval.pn["TSS","Testing.data","RF",,]

#for all
myBiomodModelEval.pn["TSS","Testing.data",,,]

#------------------------------------------------------------------#
# let's print the ROC scores of all selected models
myBiomodModelEval.pn["ROC","Testing.data",,,]

#------------------------------------------------------------------#
#an array (or a data.frame) containing models predictions over calibrating and testing data (those used for evaluate models)
names(getModelsPrediction(myBiomodModelOut.pn, as.data.frame=TRUE))
str(getModelsPrediction(myBiomodModelOut.pn, as.data.frame=TRUE))

#GLM
pn.pred.glm <- getModelsPrediction(myBiomodModelOut.pn, as.data.frame=TRUE)$Pelagia.noctiluca_AllData_RUN3_GLM

windows()
level.plot(data.in=pn.pred.glm, XY=myRespXY, color.gradient = "red", cex = 1, level.range = c(min(pn.pred.glm), max(pn.pred.glm)), show.scale = TRUE, title = "Pelagia noctiluca (GLM)", SRC=FALSE, save.file="tiff", ImageSize="large", AddPresAbs=NULL, plot=T)

#MARS
pn.pred.mars <- getModelsPrediction(myBiomodModelOut.pn, as.data.frame=TRUE)$Pelagia.noctiluca_AllData_RUN3_MARS

windows()
level.plot(data.in=pn.pred.mars, XY=myRespXY, color.gradient = "red", cex = 1, level.range = c(min(pn.pred.mars), max(pn.pred.mars)), show.scale = TRUE, title = "Pelagia noctiluca (MARS)", SRC=FALSE, save.file="tiff", ImageSize="large", AddPresAbs=NULL)

#GAM
pn.pred.GAM <- getModelsPrediction(myBiomodModelOut.pn, as.data.frame=TRUE)$Pelagia.noctiluca_AllData_RUN1_GAM

windows()
level.plot(data.in=pn.pred.GAM, XY=myRespXY, color.gradient = "red", cex = 1, level.range = c(min(pn.pred.GAM), max(pn.pred.GAM)), show.scale = TRUE, title = "Pelagia noctiluca (GAM)", SRC=FALSE, save.file="tiff", ImageSize="large", AddPresAbs=NULL)

#RF
pn.pred.RF <- getModelsPrediction(myBiomodModelOut.pn, as.data.frame=TRUE)$Pelagia.noctiluca_AllData_RUN1_RF

windows()
level.plot(data.in=pn.pred.RF, XY=myRespXY, color.gradient = "red", cex = 1, level.range = c(min(pn.pred.RF), max(pn.pred.RF)), show.scale = TRUE, title = "Pelagia noctiluca (RF)", SRC=FALSE, save.file="tiff", ImageSize="large", AddPresAbs=NULL)

#CTA
pn.pred.CTA <- getModelsPrediction(myBiomodModelOut.pn, as.data.frame=TRUE)$Pelagia.noctiluca_AllData_RUN2_CTA

windows()
level.plot(data.in=pn.pred.CTA, XY=myRespXY, color.gradient = "red", cex = 1, level.range = c(min(pn.pred.CTA), max(pn.pred.CTA)), show.scale = TRUE, title = "Pelagia noctiluca (CTA)", SRC=FALSE, save.file="tiff", ImageSize="large", AddPresAbs=NULL)

#------------------------------------------------------------------#
# Relative importance of the explanatory variables
# print variable importances
getModelsVarImport(myBiomodModelOut.pn)

pn.var.impor <- as.data.frame(getModelsVarImport(myBiomodModelOut.pn))
str(pn.var.impor)

pn.var.impor.mean <- matrix(nrow=6, ncol=5)
colnames(pn.var.impor.mean) <- c("GLM", "GAM", "CTA", "RF", "MARS")
rownames(pn.var.impor.mean) <- c("Salinity", "sstmax", "nitrate", "dissox", "chlomax", "phosphate")

head(pn.var.impor.mean)

pn.var.impor.mean[1:6,1] <- rowMeans(cbind(pn.var.impor$GLM.RUN1.AllData,pn.var.impor$GLM.RUN2.AllData,pn.var.impor$GLM.RUN3.AllData))

pn.var.impor.mean[1:6,2] <- rowMeans(cbind(pn.var.impor$GAM.RUN1.AllData,pn.var.impor$GAM.RUN2.AllData,pn.var.impor$GAM.RUN3.AllData))

pn.var.impor.mean[1:6,3] <- rowMeans(cbind(pn.var.impor$CTA.RUN1.AllData,pn.var.impor$CTA.RUN2.AllData,pn.var.impor$CTA.RUN3.AllData))

pn.var.impor.mean[1:6,4] <- rowMeans(cbind(pn.var.impor$RF.RUN1.AllData,pn.var.impor$RF.RUN2.AllData,pn.var.impor$RF.RUN3.AllData))

pn.var.impor.mean[1:6,5] <- rowMeans(cbind(pn.var.impor$MARS.RUN1.AllData,pn.var.impor$MARS.RUN2.AllData,pn.var.impor$MARS.RUN3.AllData))

head(pn.var.impor.mean)

write.table(pn.var.impor.mean, file="Var.import.pn.txt",quote=F, sep="\t", na = "NA", dec= ",", col.names=T, row.names=TRUE)

#------------------------------------------------------------------#
#------------------------------------------------------------------#
# ENSEMBLE MODELING
#combines individual models to build some kind of meta-model
myBiomodEM.pn <- BIOMOD_EnsembleModeling(
                  modeling.output = myBiomodModelOut.pn,
                  chosen.models = 'all',
                  em.by='all',
                  eval.metric = c('TSS'),
                  eval.metric.quality.threshold = c(0.5),
                  prob.mean = T,
                  prob.cv = T,
                  prob.ci = T,
                  prob.ci.alpha = 0.05,
                  prob.median = T,
                  committee.averaging = T,
                  prob.mean.weight = T,
                  prob.mean.weight.decay = 'proportional' )

#------------------------------------------------------------------#
# print summary
myBiomodEM.pn

#------------------------------------------------------------------#
# get evaluation scores
getEMeval(myBiomodEM.pn)

#------------------------------------------------------------------#
#------------------------------------------------------------------#
# Projection 
# projection over the Mediterranean under current conditions
myBiomodProj.pn <- BIOMOD_Projection(
                    modeling.output = myBiomodModelOut.pn,
                    new.env = myExpl,
                    xy.new.env = myRespXY,
                    proj.name = 'current',
                    selected.models = 'all',
                    binary.meth = 'TSS',
                    compress = 'xz',
                    clamping.mask = F,
                    output.format = '.RData')

#------------------------------------------------------------------#
# summary of crated oject
myBiomodProj.pn

#------------------------------------------------------------------#
# files created on hard drive
list.files("Pelagia.noctiluca/proj_current/")

#------------------------------------------------------------------#
# make some plots sub-selected by str.grep argument
plot(myBiomodProj.pn, str.grep = 'MARS')

pn.proj.gam <- getProjection(myBiomodProj.pn, as.data.frame=TRUE)$Pelagia.noctiluca_AllData_RUN1_GAM

windows()
level.plot(data.in=pn.proj.gam, XY=myRespXY, color.gradient = "red", cex = 1, level.range = c(min(pn.proj.gam), max(pn.proj.gam)), show.scale = TRUE, title = "Pelagia noctiluca (GAM)", SRC=FALSE, save.file="no", ImageSize="large", AddPresAbs=NULL)


#------------------------------------------------------------------#
#------------------------------------------------------------------#
# Ensemble Forcasting
#to project the meta-models you have created with BIOMOD_EnsembleModeling
myBiomodEF.pn <- BIOMOD_EnsembleForecasting(
                  projection.output = myBiomodProj.pn,
                  EM.output = myBiomodEM.pn,
                  binary.meth = 'TSS')

Ens.Forecast.pn <- load('Pelagia.noctiluca/proj_current/proj_current_Pelagia.noctiluca_TotalConsensus_EMbyTSS.RData')

x.ensmod <- myRespXY$Long
y.ensmod <- myRespXY$lat
z.ensmod <- proj_current_Pelagia.noctiluca_TotalConsensus_EMbyTSS[,"ef.mean"]
probability <- proj_current_Pelagia.noctiluca_TotalConsensus_EMbyTSS[,"ef.mean"] / 1000

ens.data.pn <- as.data.frame(cbind(x.ensmod, y.ensmod, z.ensmod, probability))

pn.ensforecat <- qplot(x=x.ensmod, y=y.ensmod,colour=probability, data=ens.data.pn, xlab="longitude", ylab="Latitude", main="P. noctiluca ensemble forecast") +
  scale_colour_gradient(low="gray", high="red",space = "Lab",na.value = "grey50", guide = "colourbar")+
  theme_bw()

windows()
pn.ensforecat

ggsave(filename="P.noctiluca.ensforcat.pdf", plot=pn.ensforecat, path=getwd(), width=20, height=20, units="cm")

#------------------------------------------------------------------#
#plotearlo sobre un archivo satelital
library("ggmap")
cat.coast <- get_map(location = c(lon=2, lat=41.5), maptype ="satellite", zoom=8, source="google")
windows()
ggmap(cat.coast)

pn.ensforecat.sat <- ggmap(cat.coast, legend='none') +
  geom_point(aes(x=x.ensmod, y=y.ensmod, colour=probability, size=1.5), data =ens.data.pn, alpha =0.5, labels="")+
  scale_colour_gradient(low="gray", high="red",space ="Lab", na.value = "grey50", guide = "colourbar")+
  scale_size_continuous(1.5, guide="none")+
  labs(title ="P. noctiluca ensemble forecast", x="Longitude", y="Latitude")+
  theme_bw()

windows()
pn.ensforecat.sat

ggsave(filename="P.noctiluca.ensforCat.sat.pdf", plot=pn.ensforecat.sat, path=getwd(), width=20, height=20, units="cm")

ggsave(filename="P.noctiluca.ensforCat.sat.jpeg", plot=pn.ensforecat.sat, path=getwd(), width=20, height=20, units="cm", dpi = 300)

#------------------------------------------------------------------#
#Recilcado para cambiar tamaño y color segun un vector
# pn.ensforecat.sat <- ggmap(cat.coast, legend='none') +
#   geom_point(aes(x=x.ensmod, y=y.ensmod, colour=probability, size=probability), data =ens.data.pn, alpha =0.5, labels="")+
#   scale_colour_gradient(low="gray", high="red",space ="Lab", na.value = "grey50", guide = "colourbar")+
#   scale_size_continuous("probability", guide="none")+
#   theme_bw()
#------------------------------------------------------------------#

#------------------------------------------------------------------#
#------------------------------------------------------------------#
#------------------------------------------------------------------#
#Plot response curves

#------------------------------------------------------------------#
#GLM
#Load the models for which we want to extract the predicted response curves
myGLMs.pn <- BIOMOD_LoadModels(myBiomodModelOut.pn, models='GLM')

# plot 2D response plots
windows()
myRespPlot2D.pn <- response.plot2(models  = myGLMs.pn, Data = getModelsInputData(myBiomodModelOut.pn,'expl.var'),show.variables= getModelsInputData(myBiomodModelOut.pn,'expl.var.names'), do.bivariate = FALSE, fixed.var.metric = 'mean',col = c("blue", "red"),legend = TRUE, data_species = getModelsInputData(myBiomodModelOut.pn,'resp.var'), save.file="pdf", name="P.noctiluca response_curve GLM", ImageSize=480, plot=TRUE)
#------------------------------------------------------------------#

#------------------------------------------------------------------#
#GAM
#Load the models for which we want to extract the predicted response curves
myGAMs.pn <- BIOMOD_LoadModels(myBiomodModelOut.pn, models='GAM')

# plot 2D response plots
windows()
myRespPlot2D.pn <- response.plot2(models  = myGAMs.pn, Data = getModelsInputData(myBiomodModelOut.pn,'expl.var'),show.variables= getModelsInputData(myBiomodModelOut.pn,'expl.var.names'), do.bivariate = FALSE, fixed.var.metric = 'mean',col = c("blue", "red"),legend = TRUE, data_species = getModelsInputData(myBiomodModelOut.pn,'resp.var'), save.file="pdf", name="P.noctiluca response_curve GAM", ImageSize=480, plot=TRUE)
#------------------------------------------------------------------#

#------------------------------------------------------------------#
#RF
#Load the models for which we want to extract the predicted response curves
myRFs.pn <- BIOMOD_LoadModels(myBiomodModelOut.pn, models='RF')

# plot 2D response plots
windows()
myRespPlot2D.pn <- response.plot2(models  = myRFs.pn, Data = getModelsInputData(myBiomodModelOut.pn,'expl.var'),show.variables= getModelsInputData(myBiomodModelOut.pn,'expl.var.names'), do.bivariate = FALSE, fixed.var.metric = 'mean',col = c("blue", "red"),legend = TRUE, data_species = getModelsInputData(myBiomodModelOut.pn,'resp.var'), save.file="pdf", name="P.noctiluca response_curve RF", ImageSize=480, plot=TRUE)
#------------------------------------------------------------------#

#------------------------------------------------------------------#
#CTA
#Load the models for which we want to extract the predicted response curves
myCTAs.pn <- BIOMOD_LoadModels(myBiomodModelOut.pn, models='CTA')

# plot 2D response plots
windows()
myRespPlot2D.pn <- response.plot2(models  = myCTAs.pn, Data = getModelsInputData(myBiomodModelOut.pn,'expl.var'),show.variables= getModelsInputData(myBiomodModelOut.pn,'expl.var.names'), do.bivariate = FALSE, fixed.var.metric = 'mean',col = c("blue", "red"),legend = TRUE, data_species = getModelsInputData(myBiomodModelOut.pn,'resp.var'), save.file="pdf", name="P.noctiluca response_curve CTA", ImageSize=480, plot=TRUE)
#------------------------------------------------------------------#

#------------------------------------------------------------------#
#MARS
#Load the models for which we want to extract the predicted response curves
myMARSs.pn <- BIOMOD_LoadModels(myBiomodModelOut.pn, models='MARS')

# plot 2D response plots
windows()
myRespPlot2D.pn <- response.plot2(models  = myMARSs.pn, Data = getModelsInputData(myBiomodModelOut.pn,'expl.var'),show.variables= getModelsInputData(myBiomodModelOut.pn,'expl.var.names'), do.bivariate = FALSE, fixed.var.metric = 'mean',col = c("blue", "red"),legend = TRUE, data_species = getModelsInputData(myBiomodModelOut.pn,'resp.var'), save.file="pdf", name="P.noctiluca response_curve MARS", ImageSize=480, plot=TRUE)
#------------------------------------------------------------------#
#------------------------------------------------------------------#



#------------------------------------------------------------------#
#------------------------------------------------------------------#
#------------------------------------------------------------------#

# Projection Over the Spanish Coast

#------------------------------------------------------------------#
#------------------------------------------------------------------#
# Projection 
# projection over the Spanish coast under current conditions
#------------------------------------------------------------------#
#Load the new environmental data
Env.sp <- read.table("Env.points.Spain.txt", header=T, dec=".")
head(Env.sp)
summary(Env.sp)

# vuelvo a quitar lo NA's
I1 <- is.na(Env.sp$Long) | is.na(Env.sp$lat) | is.na(Env.sp$Salinity) | is.na(Env.sp$sstmax) | is.na(Env.sp$nitrate) | is.na(Env.sp$dissox) | is.na(Env.sp$chlomax) | is.na(Env.sp$phosphate)

Env.sp <- Env.sp[!I1, ]

#------------------------------------------------------------------#
# the XY coordinates of species data
myRespXY.sp <- Env.sp[,c("Long","lat")]

#------------------------------------------------------------------#
# Environmental variables
myExpl.sp <- Env.sp[,c("Salinity","sstmax","nitrate", "dissox", "chlomax", "phosphate")]

windows()
level.plot(myExpl.sp$Salinity,XY=myRespXY.sp, color.gradient = "red", cex = 1, level.range = c(min(myExpl.sp$Salinity), max(myExpl.sp$Salinity)), show.scale = TRUE, title = "Salinity", SRC=FALSE, save.file="no", ImageSize="large")

windows()
qplot(x=Long, y=lat,colour=phosphate, data=Env.sp, xlab="longitude", ylab="Latitude", main="Phosphate") +
  scale_colour_gradient(low="green", high="red",space = "Lab",na.value = "grey50", guide = "colourbar")+
  theme_bw()

#------------------------------------------------------------------#
# Projection 
myBiomodProj.sp.pn <- BIOMOD_Projection(
                        modeling.output = myBiomodModelOut.pn,
                        new.env = myExpl.sp,
                        xy.new.env = myRespXY.sp,
                        proj.name = 'Spain',
                        selected.models = "all",
                        binary.meth = 'TSS',
                        compress = 'xz',
                        clamping.mask = F,
                        output.format = '.RData')


#------------------------------------------------------------------#
# summary of crated oject
myBiomodProj.sp.pn

#------------------------------------------------------------------#
# files created on hard drive
list.files("Pelagia.noctiluca/proj_Spain/")

#------------------------------------------------------------------#
# make some plots sub-selected by str.grep argument
plot(myBiomodProj.sp.pn, str.grep = 'MARS')

pn.proj.gam.sp <- getProjection(myBiomodProj.sp.pn, as.data.frame=TRUE)$Pelagia.noctiluca_AllData_RUN3_GAM

windows()
level.plot(data.in=pn.proj.gam.sp, XY=myRespXY.sp, color.gradient = "red", cex = 1, level.range = c(min(pn.proj.gam.sp), max(pn.proj.gam.sp)), show.scale = TRUE, title = "Pelagia noctiluca (GAM)", SRC=FALSE, save.file="no", ImageSize="large", AddPresAbs=NULL)

#------------------------------------------------------------------#
#------------------------------------------------------------------#
# Ensemble Forcasting
# to project the meta-models you have created with BIOMOD_EnsembleModeling
myBiomodEF.pn.sp <- BIOMOD_EnsembleForecasting(
                      projection.output = myBiomodProj.sp.pn,
                      EM.output = myBiomodEM.pn,
                      binary.meth = 'TSS')

#Cargamos las proyecciones
p.nocti.ensfore.sp <- load('Pelagia.noctiluca/proj_Spain/proj_Spain_Pelagia.noctiluca_TotalConsensus_EMbyTSS.RData')

x.ensmod.sp <- myRespXY.sp$Long
y.ensmod.sp <- myRespXY.sp$lat
z.ensmod.sp <- proj_Spain_Pelagia.noctiluca_TotalConsensus_EMbyTSS[,"ef.mean"]
probability <- proj_Spain_Pelagia.noctiluca_TotalConsensus_EMbyTSS[,"ef.mean"] / 1000
em.cv       <- proj_Spain_Pelagia.noctiluca_TotalConsensus_EMbyTSS[,"ef.cv"] 
em.median   <- proj_Spain_Pelagia.noctiluca_TotalConsensus_EMbyTSS[,"ef.median"] / 1000
em.ca       <- proj_Spain_Pelagia.noctiluca_TotalConsensus_EMbyTSS[,"ef.ca"] / 1000

ens.data.pn.sp <- as.data.frame(cbind(x.ensmod.sp, y.ensmod.sp, z.ensmod.sp, probability, em.cv, em.median, em.ca))


pn.ensforeSpain <- qplot(x=x.ensmod.sp, y=y.ensmod.sp,colour=probability, data=ens.data.pn.sp, xlab="longitude", ylab="Latitude", main="P. noctiluca ensemble forecast") +
  scale_colour_gradient(low="gray", high="red",space = "Lab",na.value = "grey50", guide = "colourbar")+
  theme_bw()

windows()
pn.ensforeSpain

ggsave(filename="P.noctiluca.ensforSpain.pdf", plot=pn.ensforeSpain, path=getwd(), width=20, height=20, units="cm")
#------------------------------------------------------------------#
#plotearlo sobre un archivo satelital
library("ggmap")
sp.coast <- get_map(location = c(lon=-1, lat=40), maptype ="satellite", zoom=6, source="google")
windows()
ggmap(sp.coast)


pn.ensforeSpain.sat <- ggmap(sp.coast, legend='bottomright') +
  geom_point(aes(x=x.ensmod.sp, y=y.ensmod.sp, colour=probability), data =ens.data.pn.sp, alpha =0.5)+
scale_colour_gradient(low="gray", high="red",space ="Lab", na.value = "grey50", guide = "colourbar")+
  labs(title ="P. noctiluca ensemble forecast", x="Longitude", y="Latitude")+
  theme_bw()

windows()
pn.ensforeSpain.sat

ggsave(filename="P.noctiluca.ensforSpain.sat.pdf", plot=pn.ensforeSpain.sat, path=getwd(), width=20, height=20, units="cm")

ggsave(filename="P.noctiluca.ensforSpain.sat.jpeg", plot=pn.ensforeSpain.sat, path=getwd(), width=20, height=20, units="cm", dpi = 300)

#------------------------------------------------------------------#
#Otro indicador
pn.ensforeSpain.ca <- qplot(x=x.ensmod.sp, y=y.ensmod.sp,colour=em.ca, data=ens.data.pn, xlab="longitude", ylab="Latitude", main="P. noctiluca ensemble forecast") +
  scale_colour_gradient(low="gray", high="red",space = "Lab",na.value = "grey50", guide = "colourbar")+
  theme_bw()

windows()
pn.ensforeSpain.ca


pn.ensforeSpain.med <- qplot(x=x.ensmod.sp, y=y.ensmod.sp,colour=em.median, data=ens.data.pn, xlab="longitude", ylab="Latitude", main="P. noctiluca ensemble forecast") +
  scale_colour_gradient(low="gray", high="red",space = "Lab",na.value = "grey50", guide = "colourbar")+
  theme_bw()

windows()
pn.ensforeSpain.med
#------------------------------------------------------------------#
#------------------------------------------------------------------#
#------------------------------------------------------------------#
