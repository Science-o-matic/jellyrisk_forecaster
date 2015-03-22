#!/bin/sh

R --no-save --args data/Italia/Italy_beaches.csv data/MyOcean/Italy/Total/italy-2009-2013-myov04-med-ingv-sal-an-fc.nc vosaline data/MyOcean/Italy/Total/italy-2009-2013-myov04-med-ingv-sal-an-fc.csv < R/Extract_italy_historical_data.R

R --no-save --args data/Italia/Italy_beaches.csv data/MyOcean/Italy/Total/italy-2009-2013-myov04-med-ingv-tem-an-fc.nc votemper data/MyOcean/Italy/Total/italy-2009-2013-myov04-med-ingv-tem-an-fc.csv < R/Extract_italy_historical_data.R

R --no-save --args data/Italia/Italy_beaches.csv data/MyOcean/Italy/Total/italy-2009-2013-myov04-med-ingv-cur-an-fc.nc vozocrtx data/MyOcean/Italy/Total/italy-2009-2013-myov04-med-ingv-cur-vozocrtx-an-fc.csv < R/Extract_italy_historical_data.R

R --no-save --args data/Italia/Italy_beaches.csv data/MyOcean/Italy/Total/italy-2009-2013-myov04-med-ingv-cur-an-fc.nc vomecrty data/MyOcean/Italy/Total/italy-2009-2013-myov04-med-ingv-cur-vomecrty-an-fc.csv < R/Extract_italy_historical_data.R
