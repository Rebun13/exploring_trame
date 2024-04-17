# Install app from local directory
pip install wheel # needed to install /local-app
pip install trame trame-vtk trame-vuetify pyvista requests
# pip uninstall vtk
pip install --extra-index-url https://wheels.vtk.org vtk-osmesa
pip install /local-app