# Trabajo de Fin de Grado

Este repositorio contiene el código fuente de la aplicación web desarrollada para el Trabajo de Fin de Grado de Ingeniería Informática de la Universidad de Málaga.

## Descripción

El objetivo de este proyecto es la obtención y procesamiento de imágenes satelitales de Sentinel 2 para la detección y posterior predicción del crecimiento de la vegetación sobre zonas de incendios forestales. Para ello se ha desarrollado un componente en la plataforma en la que trabaja el alumno, que permite la obtención de imágenes de satélite de forma automática, y un componente de procesamiento de imágenes que permite la detección de zonas de incendio y la predicción del crecimiento de la vegetación en dichas zonas.

## Despliegue

Para usar la aplicación es necesario generar un entorno virtual de Python.
Se ha usado pipenv en este caso. Los pasos a seguir pueden ejecutarse desde el `Makefile`.

```bash
pipenv run make install
```

## Bibliografía

### Vídeos

[A Short Course on Earth Observation Methods and Data](https://www.youtube.com/watch?v=Pz-96PMm5x8)

### Notebooks

[Wildfires from Satellite Images](https://notebooks.gesis.org/binder/jupyter/user/sentinel-hub-education-7qynditq/notebooks/wildfires/Wildfires%20from%20Satellite%20Images.ipynb)
