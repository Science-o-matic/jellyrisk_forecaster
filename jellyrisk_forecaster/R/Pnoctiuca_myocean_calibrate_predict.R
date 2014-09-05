### Encoding: UTF-8

###################################################
### 1: Load options and data
###################################################

library("biomod2")

# Load the historical data
historical_data <- read.table('historical-data-by-beach-2007-2010.csv', header=T)

# Species names
myRespName.pn <- c("Pelagia")

# the presence/absences data for our species
myResp.pn <- as.numeric(historical_data[,myRespName.pn])

# the XY coordinates of species data
myRespXY <- historical_data[,c("lon","lat")]

# Environmental variables
explVars <- c("temperature")  # c("sal","sstmean","nit", "chlomean", "pho")
myExpl <- data.frame(temperature=historical_data$temperature)# historical_data[, explVars]

# Formateando para Biomod
myBiomodData.pn <- BIOMOD_FormatingData(resp.var = myResp.pn,
                                        expl.var = myExpl,
                                        resp.xy = myRespXY,
                                        resp.name = myRespName.pn)


###################################################
### 2. Define Models Options using default options.
###################################################

myBiomodOption <- BIOMOD_ModelingOptions()


###################################################
### 3. Compute the models
###################################################

# TSS = True Skill Statistic
# http://www.esapubs.org/archive/appl/A021/062/appendix-B.htm
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


###################################################
### 4. Ensemble modelling
###################################################

myBiomodEM.pn <- BIOMOD_EnsembleModeling(
                  modeling.output = myBiomodModelOut.pn,
                  chosen.models = 'all',
                  em.by='all',
                  eval.metric = c('TSS'),
                  eval.metric.quality.threshold = c(0.3),  # XXX: Too low, should increase with more vars
                  prob.mean = T,
                  prob.cv = T,
                  prob.ci = T,
                  prob.ci.alpha = 0.05,
                  prob.median = T,
                  committee.averaging = T,
                  prob.mean.weight = T,
                  prob.mean.weight.decay = 'proportional')


###################################################
### 5. Projection Over the Spanish Coast
###################################################

# Load the new environmental data
Env.sp <- read.table("MyOcean/predictionData.csv", header=T, dec=".")

# vuelvo a quitar lo NA's
I1 <- is.na(Env.sp$lon) | is.na(Env.sp$lat) | is.na(Env.sp$sal) | is.na(Env.sp$temperature) | is.na(Env.sp$nit) | is.na(Env.sp$chlomean) | is.na(Env.sp$pho)
Env.sp <- Env.sp[!I1, ]

# the XY coordinates of species data
myRespXY.sp <- Env.sp[,c("lon","lat")]

# Environmental variables
myExpl.sp <- data.frame(temperature=Env.sp$temperature)# Env.sp[, explVars]

myBiomodProj.sp.pn <- BIOMOD_Projection(
                        modeling.output = myBiomodModelOut.pn,
                        new.env = myExpl.sp,
                        xy.new.env = myRespXY.sp,
                        proj.name = 'Catalonia',
                        selected.models = "all",
                        binary.meth = 'TSS',
                        compress = 'xz',
                        clamping.mask = F,
                        output.format = '.RData')


###################################################
### 6. Ensemble forecasting
###################################################

# This saves the file $pwd/Pelagia.noctiluca/proj_Spain/proj_Spain_Pelagia.noctiluca_ensemble.RData

myBiomodEF.pn.sp <- BIOMOD_EnsembleForecasting(
                      projection.output = myBiomodProj.sp.pn,
                      EM.output = myBiomodEM.pn,
                      binary.meth = 'TSS')

#Cargamos las proyecciones
p.nocti.ensfore.sp <- load('Pelagia/proj_Catalonia/proj_Catalonia_Pelagia_ensemble.RData')

x.ensmod.sp <- myRespXY.sp$lon
y.ensmod.sp <- myRespXY.sp$lat
z.ensmod.sp <- ef.out[,"Pelagia_TotalConsensus_TSS_EMmean"]
probability <- z.ensmod.sp / 1000
em.cv       <- ef.out[,"Pelagia_TotalConsensus_TSS_EMcv"]
em.median   <- ef.out[,"Pelagia_TotalConsensus_TSS_EMmedian"] / 1000
em.ca       <- ef.out[,"Pelagia_TotalConsensus_TSS_EMmedian"] / 1000


###################################################
### 7. Save data to CSV file
###################################################

data <- data.frame(
  lon=x.ensmod.sp,
  lat=y.ensmod.sp,
  prob=probability
)

write.csv(data, file="Pelagia.NoctilucaEF.csv", row.names=FALSE)
