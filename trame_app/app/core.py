import pickle
import pyvista as pv
import requests

from pyvista.trame.ui import plotter_ui
from time import time, gmtime, strftime
from trame.app import get_server
#from trame.app.file_upload import ClientFile
from trame.decorators import TrameApp, change
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.widgets import vuetify3


# ---------------------------------------------------------
# Engine class
# ---------------------------------------------------------

pv.OFF_SCREEN = True

@TrameApp()
class MyTrameApp:
    def __init__(self, file_url, file_format, server=None):
        self.server = get_server(server, client_type="vue3")
        self.pl = pv.Plotter()
        # Set state defaults
        self.state.setdefault("mesh", None)
        self.state.setdefault("download_progress", 0)
        self.state.setdefault("scalars", [])
        self.state.setdefault("scalars_options", [])
        self.state.setdefault(
            "styles", ["surface", "wireframe", "points", "points_gaussian"]
        )
        self.state.trame__title = "Trame Multi-user"
        if self.server.hot_reload:
            self.server.controller.on_server_reload.add(self._build_ui)
        self.ui = self._build_ui()
        self.handleDownload(file_url, file_format)


    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    @change("scalar_selector", "style_selector", "show_edges")
    def changeOptions(self, **kwargs):
        print(f"Volume: {self.state.volume_switch}")
        if self.state.mesh:
            self.pl.clear_actors()
            self.pl.add_mesh(
                pickle.loads(self.state.mesh),
                style=self.state.style_selector,
                scalars=self.state.scalar_selector,
                show_scalar_bar=True,
                show_edges=self.state.show_edges,
            )
    
    def handleDownload(self, file_url, file_format):
        filename = f"/home/trame-user/{time()}.{file_format}"
        with open(filename, "a+b") as file:
            query_parameters = {"downloadformat": format}
            with requests.get(file_url, params=query_parameters, stream=True) as response:
                response.raise_for_status()
                total = int(response.headers.get('content-length', 0))
                c = 0
                for chunk in response.iter_content(chunk_size=8192):
                    c += 8192
                    self.server.download_progress = min(100, round((c * 100)/total))
                    file.write(chunk)
        self.handleFile(filename)

    def handleFile(self, filepath, **kwargs):
        mesh = pv.read(filepath)
        self.state.mesh = pickle.dumps(mesh)
        self.state.scalars = mesh.array_names
        self.state.scalars_options = [
            {"title": option, "value": option}
            for option in self.state.scalars
        ]
        self.pl.add_mesh(mesh, show_scalar_bar=True)
        self.pl.reset_camera()

    def _build_ui(self, *args, **kwargs):
        with SinglePageWithDrawerLayout(self.server) as layout:
            with layout.toolbar:
                vuetify3.VSpacer()
                '''
                vuetify3.VProgressLinear(
                    label="Download progress",
                    buffer_value="0",
                    color="teal",
                    model_value=("download_progress",),
                    stream=True
                )
                '''
            with layout.drawer:
                with vuetify3.VRadioGroup(
                    v_model=("style_selector", None), label="Style"
                ):
                    for option in self.state.styles:
                        vuetify3.VRadio(label=option, value=option)
                vuetify3.VSelect(
                    v_model=("scalar_selector", None),
                    label="Scalar",
                    items=("scalars_options",),
                )
                vuetify3.VSwitch(
                    v_model=("show_edges", False),
                    label="Show edges",
                )
            with layout.content:
                with vuetify3.VContainer(
                    fluid=True,
                    classes="pa-0 fill-height",
                    style="position: relative;",
                ):
                    view = plotter_ui(self.pl)
                    self.ctrl.view_update = view.update
            # Footer
            # layout.footer.hide()

            return layout
