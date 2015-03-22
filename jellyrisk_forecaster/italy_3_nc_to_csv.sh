#!/bin/sh

R --no-save --args data/Italia/Italy_beaches_3.csv data/MyOcean/Italy/Total/italy-2009-2014-myov04-med-ingv-sal-an-fc.nc vosaline data/MyOcean/Italy/Total/italy-2009-2014-myov04-med-ingv-sal-an-fc-3.csv < R/Extract_italy_historical_data.R

R --no-save --args data/Italia/Italy_beaches_3.csv data/MyOcean/Italy/Total/italy-2009-2014-myov04-med-ingv-tem-an-fc.nc votemper data/MyOcean/Italy/Total/italy-2009-2014-myov04-med-ingv-tem-an-fc-3.csv < R/Extract_italy_historical_data.R

R --no-save --args data/Italia/Italy_beaches_3.csv data/MyOcean/Italy/Total/italy-2009-2014-myov04-med-ingv-cur-an-fc.nc vozocrtx data/MyOcean/Italy/Total/italy-2009-2014-myov04-med-ingv-cur-vozocrtx-an-fc-3.csv < R/Extract_italy_historical_data.R

R --no-save --args data/Italia/Italy_beaches_3.csv data/MyOcean/Italy/Total/italy-2009-2014-myov04-med-ingv-cur-an-fc.nc vomecrty data/MyOcean/Italy/Total/italy-2009-2014-myov04-med-ingv-cur-vomecrty-an-fc-3.csv < R/Extract_italy_historical_data.R
