# Bomberman Simulation

Este proyecto es una simulación del juego Bomberman, implementada utilizando el framework **Mesa** para modelar la simulación y **Tkinter** para la selección de mapas. Permite visualizar diferentes agentes y sus interacciones en un entorno basado en un mapa definido por el usuario.

## Características

- Visualización de agentes en un entorno gráfico.
- Carga de mapas desde archivos de texto.
- Selección de algoritmos de búsqueda a través de un menú desplegable.
- Personalización de imágenes para diferentes agentes.

## Requisitos

Asegúrate de tener Python 3.10 o superior instalado. Este proyecto utiliza las siguientes dependencias:

- Mesa
- Tkinter
- Pillow

## Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/alexander-pag/agent-jj-bomberman.git
   cd agent-jj-bomberman
   ```

2. Crea un entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias desde requirements.txt:

   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Ejecuta la simulación:

   python project/server.py

2. Se abrirá una ventana de selección de archivos donde podrás elegir el mapa a cargar.

3. Selecciona un archivo de mapa en formato .txt y haz clic en "Abrir".

4. La simulación se iniciará y podrás observar el comportamiento de los agentes en el mapa seleccionado.
