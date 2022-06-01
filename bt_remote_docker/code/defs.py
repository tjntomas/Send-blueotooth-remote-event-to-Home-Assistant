import yaml

PARAMETERS_PATH = '/config/config.yaml'

class Container(object):
    pass

def params():
    with open(PARAMETERS_PATH, 'r') as stream:
        try:
            pars = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)

    par = Container()
    for itm in pars:
        setattr(par, itm, pars[itm])   
    return par
