### Encoding: UTF-8

target_date <- commandArgs(trailingOnly=TRUE)[1]

library("biomod2")

# read model data
load(file='Pnoctiluca_model.R')


###################################################
### Projection Over the Spanish Coast
###################################################

# Load the new environmental data
Env.sp <- read.table(
  sprintf("./MyOcean/Forecast/Forecast_Env-%s.csv", target_date),
  header=T, dec="."
)

# vuelvo a quitar lo NA's
I1 <- is.na(Env.sp$lon) | is.na(Env.sp$lat) | is.na(Env.sp$sal) | is.na(Env.sp$temperature) | is.na(Env.sp$nit) | is.na(Env.sp$chlorophile) | is.na(Env.sp$pho)
Env.sp <- Env.sp[!I1, ]

# the XY coordinates of species data
myRespXY.sp <- Env.sp[,c("lon","lat")]

# Environmental variables
myExpl.sp <- Env.sp[, explVars] # data.frame(temperature=Env.sp$temperature)

proj.name <- sprintf('Catalonia-%s', target_date)
myBiomodProj.sp.pn <- BIOMOD_Projection(
                        modeling.output = myBiomodModelOut.pn,
                        new.env = myExpl.sp,
                        xy.new.env = myRespXY.sp,
                        proj.name = proj.name,
                        selected.models = "all",
                        binary.meth = 'TSS',
                        compress = 'xz',
                        clamping.mask = F,
                        output.format = '.RData')


###################################################
### Ensemble forecasting
###################################################

# This saves the file $pwd/Pelagia.noctiluca/proj_Spain/proj_Spain_Pelagia.noctiluca_ensemble.RData

myBiomodEF.pn.sp <- BIOMOD_EnsembleForecasting(
                      projection.output = myBiomodProj.sp.pn,
                      EM.output = myBiomodEM.pn,
                      binary.meth = 'TSS')

# Load projections from disk
p.nocti.ensfore.sp <- load(
  sprintf('Pelagia/proj_%s/proj_%s_Pelagia_ensemble.RData', proj.name, proj.name)
)
x.ensmod.sp <- myRespXY.sp$lon
y.ensmod.sp <- myRespXY.sp$lat
z.ensmod.sp <- ef.out[,"Pelagia_TotalConsensus_TSS_EMmean"]
probability <- z.ensmod.sp / 1000
em.cv       <- ef.out[,"Pelagia_TotalConsensus_TSS_EMcv"]
em.median   <- ef.out[,"Pelagia_TotalConsensus_TSS_EMmedian"] / 1000
em.ca       <- ef.out[,"Pelagia_TotalConsensus_TSS_EMmedian"] / 1000
em.ciSup    <- ef.out[,'Pelagia_TotalConsensus_TSS_EMciSup']/ 1000
em.ciInf    <- ef.out[,'Pelagia_TotalConsensus_TSS_EMciInf'] / 1000


###################################################
### 7. Save data to CSV file
###################################################

data <- data.frame(
  lon=x.ensmod.sp,
  lat=y.ensmod.sp,
  prob=probability,
  probsup=em.ciSup,
  probinf=em.ciInf,
  date=rep(paste(target_date, '00:00:00'), length(probability))
)

write.csv(data,
  file=sprintf("./Projections/PelagiaNoctilucaEF-%s.csv", target_date),
  row.names=FALSE
)
