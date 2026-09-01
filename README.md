# veg_conserve_ndvi
## Visualisation and mapping project: MOD13A2 using GEE
### MODIS MOD13A2 Image Collection

**Dataset:** MODIS/006/MOD13A2 (Version 6, Collection 6.1)

**Instrument:** Moderate Resolution Imaging Spectroradiometer (MODIS) on NASA Terra and Aqua satellites

**Temporal resolution:** 16-day composite (one image every 16 days)

**Spatial resolution:** 1 km (1000 m pixel size)

**Bands:** NDVI (Normalized Difference Vegetation Index), EVI (Enhanced Vegetation Index), quality flags

**Coverage:** Global, including Northern California (1 km pixel size provides regional detail while maintaining long-term historical record)

**Data availability:** 2000 to present (latest data approximately 1-2 months behind real-time due to processing lag)

**Use case:** Suitable for 10+ year vegetation trends and climate-scale changes where 1 km resolution is adequate. Monthly compositing reduces cloud contamination and atmospheric noise compared to daily observations.

File to run in GEE is: Javascript to run code directly in GEE for veg_conservation_ndvi.txt (but does not include water mask in the NDVI)

Google Colab (ndvi_dashboard_GEE.ipynb): To extract and aggregate image collection

Map for production ("vegetation_dashboard.html")

Script for producing the map ("vegetation_dashboard.py")
