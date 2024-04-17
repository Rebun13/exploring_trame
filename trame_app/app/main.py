import logging
from .core import MyTrameApp
logger = logging.getLogger(__name__)

# def main(url, fileFormat, server=None, **kwargs):
def main(server=None, **kwargs):
    #app = MyTrameApp(url, fileFormat, server)
    app = MyTrameApp("http://162.162.0.1:8000/item/example.vtk", "vtk", server)
    app.server.start(**kwargs)


if __name__ == "__main__":
    main()
