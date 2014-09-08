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
explVars <- c("temperature", "salinity", "chlorophile")  # c("sal","sstmean","nit", "chlomean", "pho")
myExpl <- historical_data[, explVars] # data.frame(temperature=historical_data$temperature)

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
                  eval.metric.quality.threshold = c(0.4),
                  prob.mean = T,
                  prob.cv = T,
                  prob.ci = T,
                  prob.ci.alpha = 0.05,
                  prob.median = T,
                  committee.averaging = T,
                  prob.mean.weight = T,
                  prob.mean.weight.decay = 'proportional')

save(myBiomodEM.pn, myBiomodModelOut.pn, explVars, file='Pnoctiluca_model.R')
