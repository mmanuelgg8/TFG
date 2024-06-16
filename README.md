# Trabajo de Fin de Grado

Este repositorio contiene el código fuente de la aplicación web desarrollada para el Trabajo de Fin de Grado de Ingeniería Informática de la Universidad de Málaga.

## Descripción

El objetivo de este proyecto es la obtención y procesamiento de imágenes satelitales de Sentinel 2 para el entrenamiento de modelos de aprendizaje automático de forma autónoma, por medio de un simple archivo de configuración.
Además de ser expansible al poder diseñar nuevos modelos y poder compararlos.

## Despliegue

Para usar la aplicación es necesario disponer de Docker activo en el sistema.
Con el uso de `make` se puede desplegar la aplicación de forma sencilla.

```bash
make run-image FILE"config.json"
```

## Bibliografía

### Vídeos

[A Short Course on Earth Observation Methods and Data](https://www.youtube.com/watch?v=Pz-96PMm5x8)

### Notebooks

[Wildfires from Satellite Images](https://notebooks.gesis.org/binder/jupyter/user/sentinel-hub-education-7qynditq/notebooks/wildfires/Wildfires%20from%20Satellite%20Images.ipynb)
