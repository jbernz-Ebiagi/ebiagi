from Ebiagi import Ebiagi
from EbiagiBase import EbiagiBase

def create_instance(*a):
    ins = Ebiagi(*a)
    with ins.component_guard():
        ins.ebiagi_base = EbiagiBase()
    return ins