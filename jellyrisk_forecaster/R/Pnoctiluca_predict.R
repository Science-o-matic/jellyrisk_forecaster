### Encoding: UTF-8

library("biomod2")

# read model data
load(file='Pnoctiluca_model.R')

###################################################
### Projection Over the Spanish Coast
###################################################

# Load the new environmental data
Env.sp <- read.table("MyOcean/predictionData.csv", header=T, dec=".")

# vuelvo a quitar lo NA's
I1 <- is.na(Env.sp$lon) | is.na(Env.sp$lat) | is.na(Env.sp$sal) | is.na(Env.sp$temperature) | is.na(Env.sp$nit) | is.na(Env.sp$chlorophile) | is.na(Env.sp$pho)
Env.sp <- Env.sp[!I1, ]

# the XY coordinates of species data
myRespXY.sp <- Env.sp[,c("lon","lat")]

# Environmental variables
myExpl.sp <- Env.sp[, explVars] # data.frame(temperature=Env.sp$temperature)

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
### Ensemble forecasting
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
