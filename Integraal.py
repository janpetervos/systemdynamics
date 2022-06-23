import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ipywidgets as widgets
from ipywidgets import VBox, Label, Layout
from IPython.display import display

# instellen opmaak visualisaties
# sns.set(style="whitegrid", rc={"figure.figsize": (8, 4)}, font="Arial", font_scale=1.0)
sns.set(style="whitegrid", rc={"figure.figsize": (8, 4)}, font_scale=1.0)
kleur = ["#EC5D57", "#51A7F9", "#70BF41", "#F39019", "#F5D327", "#AA64D6"]  # rood, blauw, groen, oranje, geel, paars
sns.set_palette(kleur)

# bepalen tijdsinstellingen integratieproces
dt = 0.5 ** 3
st = 60  # [week]
n = int(st / dt)  # [week] simulatietijd
t = np.linspace(0, st, n)  # x-as voor eventuele tijdplots

# instellen exogene vraag
orders = np.ones(n) * 100
orders_met_vraagtoename = np.ones(n) * 100
orders_met_vraagtoename[int(10 / dt):] = 200


def Euler(f, x0, t, args=None):  # integrator
    n = len(t)
    x = np.array([x0] * n)
    for i in range(n - 1):
        h = t[i + 1] - t[i]
        x[i + 1] = x[i] + h * f(x[i], t[i], args)
    return x.T


def S(stocks, t, args):  # systeem

    # uitpakken parameters
    vraagtoename, levertijd_eindproducten, levertijd_componenten, levertijd_onderdelen, levertijd_grondstoffen = args

    # uitpakken "stocks"
    backlog, voorraad_eindproducten, voorraad_componenten, voorraad_onderdelen = stocks

    # berekenen "flows" voorraad eindproducten
    levering_eindproducten = min(voorraad_eindproducten, backlog) / levertijd_eindproducten

    # berekenen "flows" backlog
    if vraagtoename:
        orders_klanten = orders_met_vraagtoename[int(t/dt)]
    else:
        orders_klanten = orders[int(t/dt)]
    verwerkte_orders = levering_eindproducten

    # berekenen "flows" voorraad componenten
    levering_componenten = voorraad_componenten / levertijd_componenten

    # berekenen "flows" voorraad onderdelen
    levering_onderdelen = voorraad_onderdelen / levertijd_onderdelen
    voorraadverschil = backlog - voorraad_eindproducten - voorraad_componenten - voorraad_onderdelen
    levering_grondstoffen = max(0, voorraadverschil / levertijd_grondstoffen)

    return np.array([orders_klanten - verwerkte_orders, levering_componenten - levering_eindproducten,  levering_onderdelen - levering_componenten, levering_grondstoffen - levering_onderdelen])


# instellen beginvoorwaarden backlog, eindproducten, componenten en onderdelen
S0 = [1200., 300., 300., 300.]

# interface voor aan- of uitzetten vraagtoename
vraag_button = widgets.Checkbox(
    value=False,
    description="Vraagtoename",
    icon='check')

# interface voor de levertijd van eindproducten
style = {'description_width': 'initial'}
levertijd_eindproducten_slider = widgets.IntSlider(
    value=3,
    min=1,
    max=10,
    step=1,
    description="Eindproducten [week]",
    orientation="horizontal",
    style=style,
    readout_format="d")

# interface voor de levertijd van componenten
levertijd_componenten_slider = widgets.IntSlider(
    value=3,
    min=1,
    max=10,
    step=1,
    description="Componenten [week]",
    orientation="horizontal",
    style=style,
    readout_format="d")

# interface voor de levertijd van onderdelen
levertijd_onderdelen_slider = widgets.IntSlider(
    value=3,
    min=1,
    max=10,
    step=1,
    description="Onderdelen [week]",
    orientation="horizontal",
    style=style,
    readout_format="d")

# interface voor de levertijd van grondstoffen
levertijd_grondstoffen_slider = widgets.IntSlider(
    value=3,
    min=1,
    max=10,
    step=1,
    description="Grondstoffen [week]",
    orientation="horizontal",
    style=style,
    readout_format="d")

# instellen user interface
label_layout = Layout(width='600px',height='30px')
tab1 = VBox([Label("Stijging van de exogene vraag op t= 10 van 100 naar 200 stuks per week",layout=label_layout), vraag_button])
tab2 = VBox(children=[levertijd_eindproducten_slider, levertijd_componenten_slider, levertijd_onderdelen_slider, levertijd_grondstoffen_slider])
tab = widgets.Tab(children=[tab1, tab2])
tab.set_title(0, "Vraagtoename")
tab.set_title(1, "Levertijden")
display(tab)

# uitvoeren simulatie en visualiseren resultaten
@widgets.interact_manual()
def plot():
    vraagtoename = vraag_button.value
    levertijd_eindproducten = levertijd_eindproducten_slider.value
    levertijd_componenten = levertijd_componenten_slider.value
    levertijd_onderdelen =  levertijd_onderdelen_slider.value
    levertijd_grondstoffen = levertijd_grondstoffen_slider.value
    parameters = (vraagtoename, levertijd_eindproducten, levertijd_componenten, levertijd_onderdelen, levertijd_grondstoffen)
    stocks = Euler(S, S0, t, args=parameters)
    backlog, voorraad_eindproducten, voorraad_componenten, voorraad_onderdelen = stocks
    totale_voorraad = voorraad_eindproducten + voorraad_componenten + voorraad_onderdelen

    # %% visualiseren stocks en flows
    fig1, ax = plt.subplots(4, 1, figsize=(8, 16), sharex="all")
    ax[0].set_title("Tijdsverloop backlog", fontweight="bold")
    ax[1].set_title("Tijdsverloop voorraden in de distributieketen", fontweight="bold")
    ax[2].set_title("Tijdsverloop totale voorraad in de distributieketen", fontweight="bold")
    ax[3].set_title("Tijdsverloop eindvraag en leveringen", fontweight="bold")
    ax[0].plot(t, backlog, label="Backlog")
    ax[1].plot(t, voorraad_eindproducten, label="Eindproducten")
    ax[1].plot(t, voorraad_componenten, label="Componenten")
    ax[1].plot(t, voorraad_onderdelen, label="Onderdelen")
    ax[2].plot(t, totale_voorraad, color=kleur[3], label="Totale voorraad")
    if vraagtoename:
        ax[3].plot(t, orders_met_vraagtoename, color=kleur[5], label="Eindvraag")
    else:
        ax[3].plot(t, orders, color=kleur[5], label="Eindvraag")
    ax[3].plot(t, voorraad_eindproducten/levertijd_eindproducten, color=kleur[2], label="Leveringen")
    ax[3].set_xlabel("Tijd [week]")
    for i in range(2):
        ax[i].set_ylabel("Voorraad [stuks]")
    ax[3].set_ylabel("Eindproducten [stuks/week]")
    for axi in ax.flat:
        axi.legend(loc="best")
    plt.tight_layout()
    plt.show()

    # %% visualiseren fasediagrammen van schakels in de distributieketen
    fig5, ax = plt.subplots(1, 3, figsize=(12, 4))
    ax[0].plot(voorraad_eindproducten, voorraad_componenten, color=kleur[0])
    ax[1].plot(voorraad_eindproducten, voorraad_onderdelen, color=kleur[1])
    ax[2].plot(voorraad_componenten, voorraad_onderdelen, color=kleur[2])
    ax[0].set_xlabel("Eindproducten [stuks]")
    ax[0].set_ylabel("Componenten [stuks]")
    ax[1].set_xlabel("Eindproducten [stuks]")
    ax[1].set_ylabel("Onderdelen [stuks]")
    ax[2].set_xlabel("Componenten [stuks]")
    ax[2].set_ylabel("Onderdelen [stuks]")
    plt.tight_layout()
    plt.show()
