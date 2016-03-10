#----------------------------------------------------#
## MEd-Jelly - Modelos  TUNISIA ##
#----------------------------------------------------#
#----------------------------------------------------#
#setwd("/home/antoniocanepa/Documentos/PROYECTOS/ICM/GRUPO MEDUSAS/PROYECTOS/MEDJELLY-ENPI/FORECASTING/TUNISIA/Analysis_R")
setwd("/home/jellyrisk/jellyrisk_forecaster/jellyrisk_forecaster/tunez_test/data")
getwd()
#----------------------------------------------------#
#Cargamos historial
load("Tunisia_MedJellyRisk_Rpulmo.RData") # 
target_date <- commandArgs(trailingOnly=TRUE)[1]
#Cargamos paquetes a utilizar
library("biomod2")
library("ggplot2")
library("ggmap")
library('mgcv')

#Guardamos historial
save.image("Tunisia_MedJellyRisk_Rpulmo.RData")
#savehistory(file = "CF_17_Environmental_DB.Rhistory") # Save all executed commamds (not good for try and test)

#Limpiamos
#rm(list=ls())

#Salimos
#q(save="no")
#----------------------------------------------------#
#----------------------------------------------------#
Data.Tu <-  read.csv("DB_MODELO_TUNEZ_2013-2015.csv", header=T, dec=",", sep = "\t")
head(Data.Tu)
str(Data.Tu)
names(Data.Tu)

# Selecting only the species and postion data
str(Data.Tu)
Data.Tu <- Data.Tu[,c(1:16)]
head(Data.Tu)

#----------------------------------------------------#
# loading the Environmental (non collineal) variables
Data.Tu.env <-  read.csv("Models_Envar.Data.csv", header=T, dec=".", sep = ",")
#				  Data.Tu.env <-  read.csv("Models_Envar.Data.csv", header=T, dec=",", sep = "\t")
colnames(Data.Tu.env) <- c('SST', 'Sal','Chla', 'Phosphate', 'Wind.Dir.east', 'Wind.Dir.north','Wind.speed','Curr.Dir.East','Curr.Dir.North','Current.Speed','Pcb')

head(Data.Tu.env)
dim(Data.Tu.env)

#----------------------------------------------------#
# aggregating both databases
Data.Tunez.biomod <- cbind(Data.Tu, Data.Tu.env)
head(Data.Tunez.biomod)
#----------------------------------------------------#
#----------------------------------------------------#
#----------------------------------------------------#
#------------------------------------------------------------------#
# TUNEZ - biomod2 - COTYLORHYZA TUBERCULATA
#------------------------------------------------------------------#
#------------------------------------------------------------------#

#------------------------------------------------------------------#
#Load the presence of the species removing the rows containing NA
DataSpecies <- Data.Tunez.biomod[complete.cases(Data.Tunez.biomod),]
head(DataSpecies)
str(DataSpecies)
summary(DataSpecies)

# Removing species with NO records (Ch, Af, Pphy)
summary(DataSpecies)
DataSpecies <- DataSpecies[, -c(13,14,16)]


#------------------------------------------------------------------#
#------------------------------------------------------------------#
# COTYLORHYZA TUBERCULATA
#------------------------------------------------------------------#
#------------------------------------------------------------------#
# the name of studied species
myRespName <- "Rp"

#------------------------------------------------------------------#
# the presence/absences data for our species
myResp <- as.numeric(DataSpecies[,myRespName])

#------------------------------------------------------------------#
# the XY coordinates of species data
myRespXY <- DataSpecies[,c("Long","Lat")]

#------------------------------------------------------------------#
# Environmental variables
myExpl <- DataSpecies[,c('SST', 'Sal','Chla', 'Phosphate', 'Wind.Dir.east', 'Wind.Dir.north','Wind.speed','Curr.Dir.East','Curr.Dir.North','Current.Speed','Pcb')]

#x11()
#level.plot(data.in=myResp, XY=myRespXY, color.gradient = "red", cex = 1, level.range = c(min(myResp), max(myResp)), show.scale = TRUE, title = "Rhizostoma pulmo", SRC=FALSE, save.file="no", ImageSize="large", AddPresAbs=NULL)

#------------------------------------------------------------------#
# Formateando para Biomod
myBiomodData <- BIOMOD_FormatingData(resp.var = myResp,
                                        expl.var = myExpl,
                                        resp.xy = myRespXY,
                                        resp.name = myRespName)

#------------------------------------------------------------------#
# check whether the data are correctly formatted
myBiomodData

#x11()
#plot(myBiomodData)
#------------------------------------------------------------------#
# Defining Models Options using default options.
myBiomodOption <- BIOMOD_ModelingOptions(
  GLM = list( type = 'quadratic',
              interaction.level = 0,
              myFormula = NULL,
              test = 'BIC',
              family = 'poisson',
              control = glm.control(epsilon = 1e-08, 
                                    maxit = 1000, 
                                    trace = FALSE) ),
  
  GAM = list(family='poisson', k=5),
  
)

#------------------------------------------------------------------#
#------------------------------------------------------------------#
# Computing the models
myBiomodModelOut <- BIOMOD_Modeling(myBiomodData,
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
                                       modeling.id = paste(myRespName,"FirstModeling",sep=""))

#------------------------------------------------------------------#
# have a look at some outputs:  modeling summary
myBiomodModelOut
#------------------------------------------------------------------#
#------------------------------------------------------------------#
# ENSEMBLE MODELING
#combines individual models to build some kind of meta-model
myBiomodEM <- BIOMOD_EnsembleModeling(
  modeling.output = myBiomodModelOut,
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
myBiomodEM

#------------------------------------------------------------------#
#------------------------------------------------------------------#
# Projection 
# projection over the Mediterranean under current conditions
myBiomodProj <- BIOMOD_Projection(
  modeling.output = myBiomodModelOut,
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
myBiomodProj
#------------------------------------------------------------------#
# make some plots using average of projections

# GAM average
proj.gam <- rowMeans(cbind(get_predictions(myBiomodProj, as.data.frame=TRUE)$Rp_AllData_RUN1_GAM, get_predictions(myBiomodProj, as.data.frame=TRUE)$Rp_AllData_RUN2_GAM, get_predictions(myBiomodProj, as.data.frame=TRUE)$Rp_AllData_RUN3_GAM))/1000

#x11()
#level.plot(data.in=proj.gam, XY=myRespXY, color.gradient = "red", cex = 1, level.range = c(min(proj.gam), max(proj.gam)), show.scale = TRUE, title = "Rhizostoma pulmo Projection \n (GAM)", SRC=FALSE, save.file="no", ImageSize="large", AddPresAbs=NULL)


#------------------------------------------------------------------#
#------------------------------------------------------------------#
# Ensemble Forcasting
#to project the meta-models you have created with BIOMOD_EnsembleModeling
myBiomodEF <- BIOMOD_EnsembleForecasting(
  EM.output = myBiomodEM,
  projection.output = myBiomodProj)

str(myBiomodEF)
myBiomodEF

#x11()
#plot(myBiomodEF)

Ens.Forecast <- get_predictions(myBiomodEF, as.data.frame=TRUE)
names(Ens.Forecast)
colnames(Ens.Forecast) <- c('Ensemble_Mean','Ensemble_CV','Ensemble_ciInf','Ensemble_ciSup','Ensemble_Median','Ensemble_ca','Ensemble_WMean')

head(Ens.Forecast)

# Dividing the probability by 1000 to have predictions between 0-1
Ens.Forecast <- Ens.Forecast/1000 
head(Ens.Forecast)

# Ading the spatial coordinates to the ensemble modeling
Ens.Forecast$Long <- myRespXY$Long 
Ens.Forecast$Lat <- myRespXY$Lat 

#x11()
#qplot(x=Long, y=Lat, colour=Ensemble_Mean, data=Ens.Forecast, xlab="longitude", ylab="Latitude", main="R. pulmo ensemble forecast") +
#  scale_colour_gradient(low="gray", high="red",space = "Lab",na.value = "grey50", guide = "colourbar")+
#  theme_bw()

data_to_write <- data.frame(
	lon=Ens.Forecast$Long,
	lat=Ens.Forecast$Lat,
	prob=Ens.Forecast$Ensemble_Mean,
	probsup=Ens.Forecast$Ensemble_ciSup,
	probinf=Ens.Forecast$Ensemble_ciInf,
	date=rep(paste(target_date, '00:00:00'), length(Ens.Forecast$Long))
			     )

write.csv(data_to_write,
	    file=sprintf("./Projections/RpulmoEF-%s.csv", target_date),
	      row.names=FALSE
	    )


#------------------------------------------------------------------#
#plotearlo sobre un archivo satelital
library("ggmap")
Tunisia.coast <- get_map(location = c(lon=10.38, lat=36.2), maptype ="hybrid", zoom=8, source="google")

#x11()
#ggmap(Tunisia.coast)

ensforecast.sat <- 
  ggmap(Tunisia.coast, legend='none') +
  geom_point(aes(x=Long, y=Lat, colour=Ensemble_Mean, size=1.5), data= Ens.Forecast, alpha= 0.9, labels="")+
  scale_colour_gradient(low="gray", high="red",space ="Lab", na.value = "grey50", guide = "colourbar")+
  scale_size_continuous(1.5, guide="none")+
  labs(title ="R. pulmo ensemble forecast", x="Longitude", y="Latitude", colour="Mean\nProbability")+
  theme_bw()

#x11()
#ensforecast.sat

ggsave(filename="R.pulmo.Ensforcast.sat.jpeg", plot=ensforecast.sat, path=getwd(), width=20, height=20, units="cm", dpi = 300)

#------------------------------------------------------------------#
#------------------------------------------------------------------#


#Plot response curves

#------------------------------------------------------------------#
#GLM 2D
#Load the models for which we want to extract the predicted response curves
myGLMs <- BIOMOD_LoadModels(myBiomodModelOut, models='GLM')
myGLMs1 <- BIOMOD_LoadModels(myBiomodModelOut)
myGLMs2 <- BIOMOD_LoadModels(myBiomodModelOut, models=c('GLM', 'GAM'))
# plot 2D response plots
#x11()
#myRespPlot2D <- response.plot2(models  = myGLMs,
#                                  Data = get_formal_data(myBiomodModelOut,'expl.var'), 
#                                  show.variables= get_formal_data(myBiomodModelOut,'expl.var.names'),
#                                  do.bivariate = F,
#                                  fixed.var.metric = 'median',
#                                  col = c("blue", "red", "darkgreen"),
#                                  legend = TRUE,
#                                  data_species = get_formal_data(myBiomodModelOut,'resp.var'))

#x11()
#myRespPlot2D1 <- response.plot2(models  = myGLMs1,
#                                   Data = get_formal_data(myBiomodModelOut,'expl.var'), 
#                                   show.variables= get_formal_data(myBiomodModelOut,'expl.var.names'),
#                                   do.bivariate = F,
#                                   fixed.var.metric = 'median',
#                                   col = c(1:length(myGLMs1)),
#                                   legend = TRUE,
#                                   data_species = get_formal_data(myBiomodModelOut,'resp.var'))

#x11()
#myRespPlot2D2 <- response.plot2(models  = myGLMs2,
#                                   Data = get_formal_data(myBiomodModelOut,'expl.var'), 
#                                   show.variables= get_formal_data(myBiomodModelOut,'expl.var.names'),
 #                                  do.bivariate = F,
 #                                  fixed.var.metric = 'median',
 #                                  col = c(1:length(myGLMs2)),
 #                                  legend = TRUE,
 #                                  data_species = get_formal_data(myBiomodModelOut,'resp.var'))

#------------------------------------------------------------------#
